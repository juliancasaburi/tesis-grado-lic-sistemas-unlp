import { S3Client, GetObjectCommand, PutObjectCommand } from "@aws-sdk/client-s3";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";
import { promises as fsp } from "fs";

const s3Client = new S3Client();

export const handler = async (event) => {
  const { segment, destBucket } = event;
  const tempFilePath = path.join("/tmp", path.basename(segment));
  const outputFilePath = path.join("/tmp", `${path.basename(segment, path.extname(segment))}_processed.mp4`);
  
  const processedKey = path.join(segment.split(path.sep)[0], `${path.basename(segment, path.extname(segment))}_processed.mp4`);

  try {
    const response = await s3Client.send(new GetObjectCommand({
      Bucket: destBucket,
      Key: segment,
    }));

    await streamToFile(response.Body, tempFilePath);

    // Run the FFmpeg command for re-encoding
    await runFFmpeg(tempFilePath, outputFilePath);

    // Read the processed file and upload it back to S3
    const outputBuffer = await fsp.readFile(outputFilePath);
    
    await s3Client.send(new PutObjectCommand({
      Bucket: destBucket,
      Key: processedKey,
      Body: outputBuffer,
      ContentType: "video/mp4"
    }));

    return { processedKey };

  } catch (err) {
    console.error("Error processing part:", err);
    throw new Error("Part processing failed");
  }
  // Clean up the temporary files
  finally {
    fs.unlinkSync(tempFilePath);
    fs.unlinkSync(outputFilePath);
  }
};

const streamToFile = (stream, filePath) => new Promise((resolve, reject) => {
  const writeStream = fs.createWriteStream(filePath);
  stream.pipe(writeStream);
  writeStream.on("finish", resolve);
  writeStream.on("error", reject);
});

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
