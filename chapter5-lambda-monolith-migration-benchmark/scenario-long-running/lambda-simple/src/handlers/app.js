import { S3Client, GetObjectCommand, PutObjectCommand } from "@aws-sdk/client-s3";
import { spawn } from 'child_process';
import fs from 'fs';
import { promises as fsp } from 'fs';
import path from 'path';

const client = new S3Client();

export const handler = async (event) => {
  const srcBucket = event.Records[0].s3.bucket.name;
  const srcKey = decodeURIComponent(event.Records[0].s3.object.key.replace(/\+/g, ' '));
  
  const destBucket = process.env.OUTPUT_BUCKET;
  const tempFilePath = path.join('/tmp', path.basename(srcKey));

  try {
    // Retrieve the original file from the S3 bucket and save it to /tmp
    await getFileFromS3(srcBucket, srcKey, tempFilePath);
    
    // Call FFmpeg to re-encode the MP4 with reduced quality
    const outputBuffer = await runFFmpeg(tempFilePath);

    // Upload the re-encoded file to the destination S3 bucket
    await client.send(new PutObjectCommand({
      Bucket: destBucket,
      Key: srcKey,
      Body: outputBuffer,
      ContentType: 'video/mp4'
    }));

    console.log(`Successfully re-encoded and uploaded: ${srcKey}`);
    return { statusCode: 200, body: 'Success' };
    
  } catch (err) {
    console.error(err);
    const message = `Error processing ${srcKey} from bucket ${srcBucket}`;
    console.error(message);
    throw new Error(message);
  } finally {
    // Clean up the temporary file
    await fsp.unlink(tempFilePath).catch(err => console.error('Error deleting temp file:', err));
  }
};

// Function to retrieve the file from S3 and save it to /tmp
const getFileFromS3 = async (bucket, key, downloadPath) => {
  const command = new GetObjectCommand({ Bucket: bucket, Key: key });
  const response = await client.send(command);
  const fileStream = response.Body;

  return new Promise((resolve, reject) => {
    const writeStream = fs.createWriteStream(downloadPath);
    fileStream.pipe(writeStream);
    fileStream.on('end', resolve);
    fileStream.on('error', reject);
  });
};

// Function to call FFmpeg for re-encoding
const runFFmpeg = (inputFilePath) => {
  return new Promise((resolve, reject) => {
    const ffmpeg = spawn('/opt/bin/ffmpeg', [
      '-i', inputFilePath,  // Input file path
      '-vcodec', 'libx264', // Video codec
      '-crf', '28', // Reduce quality (higher value = lower quality)
      '-preset', 'slow', // Preset for better compression
      '-movflags', 'frag_keyframe+empty_moov',
      '-f', 'mp4', // Output format
      'pipe:1' // Output goes to stdout (via pipe)
    ]);

    const outputBuffer = [];

    ffmpeg.stdout.on('data', (data) => {
      outputBuffer.push(data);
    });

    ffmpeg.stderr.on('data', (data) => {
      console.error(`FFmpeg stderr: ${data}`);
    });

    ffmpeg.on('close', (code) => {
      if (code === 0) {
        resolve(Buffer.concat(outputBuffer));
      } else {
        reject(new Error(`FFmpeg process exited with code ${code}`));
      }
    });
  });
};
