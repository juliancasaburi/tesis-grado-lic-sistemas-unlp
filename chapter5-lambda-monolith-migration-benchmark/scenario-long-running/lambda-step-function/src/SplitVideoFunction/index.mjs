import {
  S3Client,
  GetObjectCommand,
  PutObjectCommand,
} from "@aws-sdk/client-s3";
import { spawn } from "child_process";
import fs from "fs";
import { promises as fsp } from "fs";
import path from "path";

const client = new S3Client();

export const handler = async (event) => {
  const srcBucket = event.bucket;
  const srcKey = event.key;
  const destBucket = event.destBucket;
  const baseFileName = path.basename(srcKey, path.extname(srcKey)); // Get the file name without extension
  const tempFilePath = path.join("/tmp", path.basename(srcKey));
  const segment_time = 300; // 5 minutes in seconds

  try {
    // Retrieve the original file from the S3 bucket and save it to /tmp
    await getFileFromS3(srcBucket, srcKey, tempFilePath);

    // Create a directory to store the video segments
    await fsp.mkdir("/tmp/segments", { recursive: true });

    // Split the video into segments of 5 minutes each
    const segments = await splitVideo(tempFilePath, baseFileName, segment_time);

    // Upload each segment to the destination S3 bucket
    const segmentUploadPromises = segments.map(async (segment) => {
      const segmentKey = `${baseFileName}/${segment.name}`;
      await client.send(
        new PutObjectCommand({
          Bucket: destBucket,
          Key: segmentKey,
          Body: segment.data,
          ContentType: "video/mp4",
        })
      );
      console.log(`Successfully uploaded segment: ${segmentKey}`);

      return segmentKey;
    });

    const uploadedSegments = await Promise.all(segmentUploadPromises);

    return {
      statusCode: 200,
      body: "Success",
      segments: uploadedSegments,
    };

  } catch (err) {
    console.error(err);
    const message = `Error processing ${srcKey} from bucket ${srcBucket}: ${err.message}`;
    console.error(message);
    throw new Error(message);
  }
  // cleanup
  finally {
    fs.unlinkSync(tempFilePath);
    const files = await fsp.readdir("/tmp/segments");
    for (const file of files) {
      const filePath = path.join("/tmp/segments", file);
      fs.unlinkSync(filePath);
    }
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
    fileStream.on("end", resolve);
    fileStream.on("error", reject);
  });
};

// Function to split the video into segment_time seconds segments
const splitVideo = async (inputFilePath, baseFileName, segment_time) => {
  return new Promise((resolve, reject) => {
    const ffmpeg = spawn("/opt/bin/ffmpeg", [
      "-i",
      inputFilePath,
      "-c",
      "copy", // Copy codecs (no re-encoding)
      "-f",
      "segment", // Use segmenter
      "-segment_time",
      segment_time,
      "-reset_timestamps",
      "1", // Reset timestamps for each segment
      "-map",
      "0", // Map all streams
      `/tmp/segments/${baseFileName}_%03d.mp4`, // Output pattern for segments
    ]);

    ffmpeg.stderr.on("data", (data) => {
      console.error(`FFmpeg stderr: ${data}`);
    });

    ffmpeg.on("close", async (code) => {
      if (code !== 0) {
        return reject(new Error(`FFmpeg process exited with code ${code}`));
      }

      try {
        const segments = [];
        const files = await fsp.readdir("/tmp/segments");
        for (const file of files) {
          if (
            file.startsWith(baseFileName) &&
            file.endsWith(".mp4")
          ) {
            const filePath = path.join("/tmp/segments", file);
            const data = await fsp.readFile(filePath);
            segments.push({ name: file, data });
          }
        }
        resolve(segments);
      } catch (error) {
        reject(new Error(`Error reading or deleting segment files: ${error.message}`));
      }
    });
  });
};

