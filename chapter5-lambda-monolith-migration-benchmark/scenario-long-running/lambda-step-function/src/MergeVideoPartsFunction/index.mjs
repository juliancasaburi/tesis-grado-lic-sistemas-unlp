import { S3Client, GetObjectCommand, PutObjectCommand } from "@aws-sdk/client-s3";
import { spawn } from 'child_process';
import { promises as fsp } from 'fs';
import path from 'path';

const client = new S3Client();

export const handler = async (event) => {
  const segments = event.processedKeys.map(keyObj => keyObj.processedKey);  // Extract processedKey from each object
  const destBucket = event.destBucket;
  const bucket = event.bucket;
  const outputFileExtension = segments[0].split('.').pop();  // Extract file extension from the first segment
  const outputFileName = segments[0].split(path.sep)[0] + '.' + outputFileExtension; // Name for the final merged file, based on original filename
  const tempFilePath = path.join('/tmp', outputFileName);
  
  try {
    // Download video segments from S3 and save locally
    const segmentPaths = await Promise.all(segments.map(async (segment, index) => {
      const response = await client.send(new GetObjectCommand({
        Bucket: bucket,
        Key: segment,
      }));
      
      const segmentPath = path.join('/tmp', `segment_${index}.${outputFileExtension}`);
      const writeStream = fsp.writeFile(segmentPath, await streamToBuffer(response.Body));
      await writeStream;
      return segmentPath;
    }));

    // Create a file list for ffmpeg
    const fileListPath = path.join('/tmp', 'filelist.txt');
    await createFileList(segmentPaths, fileListPath);
    
    // Merge the video segments
    await mergeVideos(fileListPath, tempFilePath);

    // Upload the merged video to S3
    await client.send(new PutObjectCommand({
      Bucket: destBucket,
      Key: outputFileName,
      Body: await fsp.readFile(tempFilePath),
      ContentType: 'video/mp4'
    }));

    console.log(`Successfully merged and uploaded: ${outputFileName}`);
    return { statusCode: 200, body: 'Success' };
    
  } catch (err) {
    console.error(err);
    throw new Error(`Error merging video parts: ${err.message}`);
  }
  // Clean up the temporary files
  finally {
    await fsp.unlink(tempFilePath);
  }
};

// Helper function to convert stream to buffer
const streamToBuffer = async (stream) => {
  const chunks = [];
  for await (let chunk of stream) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks);
};

// Function to create a file list for ffmpeg
const createFileList = async (segmentPaths, fileListPath) => {
  const fileListContent = segmentPaths.map(segmentPath => `file '${segmentPath}'`).join('\n');
  await fsp.writeFile(fileListPath, fileListContent);
};

// Function to merge videos using ffmpeg
const mergeVideos = (fileListPath, outputFilePath) => {
  return new Promise((resolve, reject) => {
    const ffmpeg = spawn('/opt/bin/ffmpeg', [
      '-f', 'concat', 
      '-safe', '0',
      '-i', fileListPath,
      '-c', 'copy', 
      outputFilePath
    ]);

    ffmpeg.stderr.on('data', (data) => {
      console.error(`FFmpeg stderr: ${data}`);
    });

    ffmpeg.on('close', (code) => {
      if (code !== 0) {
        return reject(new Error(`FFmpeg process exited with code ${code}`));
      }
      resolve();
    });
  });
};
