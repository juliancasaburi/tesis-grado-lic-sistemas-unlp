import { S3Client, GetObjectCommand, PutObjectCommand } from "@aws-sdk/client-s3";
import { SQSClient, ReceiveMessageCommand, DeleteMessageCommand } from "@aws-sdk/client-sqs";
import { AutoScalingClient, SetInstanceProtectionCommand } from "@aws-sdk/client-auto-scaling";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";
import { promises as fsp } from "fs";
import axios from 'axios';

// Configuration
const QUEUE_URL = process.env.QUEUE_URL;
const OUTPUT_BUCKET = process.env.OUTPUT_BUCKET;
const AUTO_SCALING_GROUP_NAME = process.env.AUTO_SCALING_GROUP_NAME;
const REGION = process.env.AWS_REGION;
const TEMP_DIR = "/tmp";

// Flag to prevent polling while processing
let isProcessing = false;

// Function to create a client directly using the EC2 instance role
const createClient = (ServiceClient) => {
    return new ServiceClient({
        region: REGION,
    });
};

// Function to fetch EC2 instance ID using metadata service
const getInstanceId = async () => {
    try {
        const tokenResponse = await axios.put('http://169.254.169.254/latest/api/token', null, {
            headers: {
                'X-aws-ec2-metadata-token-ttl-seconds': '21600'
            }
        });
        const token = tokenResponse.data;

        const response = await axios.get('http://169.254.169.254/latest/meta-data/instance-id', {
            headers: {
                'X-aws-ec2-metadata-token': token
            }
        });
        return response.data;
    } catch (error) {
        console.error("Error fetching EC2 instance ID:", error);
        throw error;
    }
};

// Function to set instance protection
const setInstanceProtection = async (instanceId, protect) => {
    const autoscalingClient = createClient(AutoScalingClient);

    const params = {
        InstanceIds: [instanceId],
        AutoScalingGroupName: AUTO_SCALING_GROUP_NAME,
        ProtectedFromScaleIn: protect,
    };

    try {
        await autoscalingClient.send(new SetInstanceProtectionCommand(params));
        console.log(`Instance protection set to ${protect} for instance ${instanceId}`);
    } catch (error) {
        console.error("Error setting instance protection:", error);
    }
};

// Function to process video
const processVideo = async (bucket, key) => {
    const startTime = Date.now();  // Log start time
    console.log(`Started processing video: ${key} at ${new Date(startTime).toISOString()}`);

    const decodedKey = decodeURIComponent(key.replace(/\+/g, " "));
    const tempFilePath = path.join(TEMP_DIR, path.basename(decodedKey));
    const outputFilePath = path.join(TEMP_DIR, `${path.basename(decodedKey, path.extname(decodedKey))}_processed.mp4`);

    // Get EC2 instance ID from metadata
    const instanceId = await getInstanceId();

    // Set instance protection before processing
    await setInstanceProtection(instanceId, true);

    try {
        // Create S3 client directly using the instance role
        const s3Client = createClient(S3Client);

        // Get video file from S3
        const response = await s3Client.send(new GetObjectCommand({
            Bucket: bucket,
            Key: decodedKey,
        }));
        await streamToFile(response.Body, tempFilePath);

        // Run the FFmpeg command for re-encoding
        await runFFmpeg(tempFilePath, outputFilePath);

        // Read the processed file and upload it back to S3
        const outputBuffer = await fsp.readFile(outputFilePath);
        await s3Client.send(new PutObjectCommand({
            Bucket: OUTPUT_BUCKET,
            Key: decodedKey,
            Body: outputBuffer,
            ContentType: "video/mp4",
        }));

        console.log(`Processed and uploaded: ${decodedKey}`);
    } catch (err) {
        console.error("Error processing video:", err);
    } finally {
        // Clean up temp files
        await fsp.unlink(tempFilePath).catch(() => {});
        await fsp.unlink(outputFilePath).catch(() => {});

        // Remove instance protection after processing
        await setInstanceProtection(instanceId, false);
        // Mark processing as finished
        isProcessing = false;

        const endTime = Date.now();  // Log end time
        const timeTaken = (endTime - startTime) / 1000;  // Calculate time taken in seconds
        console.log(`Finished processing video: ${key} at ${new Date(endTime).toISOString()}`);
        console.log(`Total time taken for processing and uploading: ${timeTaken.toFixed(2)} seconds`);
    }
};


// Utility function to save a stream to a file
const streamToFile = (stream, filePath) => new Promise((resolve, reject) => {
    const writeStream = fs.createWriteStream(filePath);
    stream.pipe(writeStream);
    writeStream.on("finish", resolve);
    writeStream.on("error", reject);
});

// Function to run FFmpeg
const runFFmpeg = (inputFilePath, outputFilePath) => new Promise((resolve, reject) => {
    const ffmpeg = spawn('/opt/bin/ffmpeg', [
        '-i', inputFilePath,
        '-vcodec', 'libx264',
        '-crf', '28',
        '-preset', 'slow',
        '-movflags', 'frag_keyframe+empty_moov',
        '-loglevel', 'quiet',
        '-f', 'mp4',
        outputFilePath
    ]);

    ffmpeg.on("close", (code) => {
        if (code === 0) {
            resolve();
        } else {
            reject(new Error(`FFmpeg error with code: ${code}`));
        }
    });
});

// Function to poll SQS for messages
const pollQueue = async () => {
    if (isProcessing) {
        console.log("Currently processing, skipping polling for new messages.");
        return;
    }

    try {
        const sqsClient = createClient(SQSClient);

        const data = await sqsClient.send(new ReceiveMessageCommand({
            QueueUrl: QUEUE_URL,
            MaxNumberOfMessages: 1,
            WaitTimeSeconds: 20,
        }));

        if (data.Messages && data.Messages.length > 0) {
            console.log(`Received ${data.Messages.length} message(s).`);

            for (const message of data.Messages) {
                const { Body, ReceiptHandle } = message;
                const { Records } = JSON.parse(Body);
                const { bucket, object } = Records[0].s3;
                const bucketName = bucket.name;
                const key = object.key;

                console.log(`Processing video from bucket: ${bucketName}, key: ${key}`);

                // Mark processing as in progress
                isProcessing = true;
                await processVideo(bucketName, key);

                // Delete the message from the queue after processing
                await sqsClient.send(new DeleteMessageCommand({
                    QueueUrl: QUEUE_URL,
                    ReceiptHandle,
                }));
            }
        } else {
            console.log("No messages to process.");
        }
    } catch (err) {
        console.error("Error polling queue:", err);
    }
};

// Start polling the SQS queue
const startPolling = () => {
    console.log("Starting SQS polling...");
    setInterval(pollQueue, 10000); // Poll every 10 seconds
};

startPolling();
