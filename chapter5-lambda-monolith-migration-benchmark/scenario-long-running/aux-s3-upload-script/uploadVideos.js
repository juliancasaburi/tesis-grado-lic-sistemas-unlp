const fs = require('fs');
const fsPromises = require('fs').promises;
const path = require('path');
const readline = require('readline');
const { S3Client, CopyObjectCommand } = require('@aws-sdk/client-s3');
const { Upload } = require('@aws-sdk/lib-storage');
const cliProgress = require('cli-progress');

// Create an interface for user input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

let s3;
let copyInterval;

// Initialize the progress bar
const progressBar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);

const totalDuration = 1800000;
const progressUpdateInterval = 1000;

// Function to copy the video in S3
const copyVideo = async (bucketName, baseKey) => {
    // Get the original extension
    const originalExtension = path.extname(baseKey);
    // Get the base name without the extension
    const baseName = path.basename(baseKey, originalExtension);
    
    // Create a new key with the timestamp and the original extension
    const newKey = `${baseName}_${Date.now()}${originalExtension}`;
    
    const encodedBaseKey = encodeURIComponent(baseKey);
    const copyParams = {
        Bucket: bucketName,
        CopySource: `/${bucketName}/${encodedBaseKey}`,
        Key: newKey,
    };

    console.log(`/${bucketName}/${baseKey}`)
    console.log(newKey)

    try {
        const copyCommand = new CopyObjectCommand(copyParams);
        await s3.send(copyCommand);
        console.log(`Copied to ${newKey} in ${bucketName}`);
    } catch (error) {
        console.error(`Error copying to ${newKey}:`, error);
    }
};

const runActivityCycle = (bucketName, baseKey, remainingTime) => {
    const logWithTime = (message) => {
        // Clear the line to avoid overlapping with the progress bar
        process.stdout.clearLine();
        process.stdout.cursorTo(0);
        console.log(`[${new Date().toLocaleTimeString()}] ${message}`);
    };

    if (remainingTime <= 0) {
        logWithTime('Test duration completed. Stopping.');
        return;
    }

    // High Activity: 1 copy per second for 10 seconds
    logWithTime('High activity phase started.');
    copyInterval = setInterval(() => copyVideo(bucketName, baseKey), 1000);
    setTimeout(() => {
        clearInterval(copyInterval);
        logWithTime('Switched to medium activity phase.');

        // Medium Activity: 1 copy every 5 seconds for 60 seconds
        copyInterval = setInterval(() => copyVideo(bucketName, baseKey), 5000);
        setTimeout(() => {
            clearInterval(copyInterval);
            logWithTime('Switched to idle phase.');

            // No Activity: No copies for 1 minute
            setTimeout(() => {
                logWithTime('Cycle complete. Restarting cycle.');
                runActivityCycle(bucketName, baseKey, remainingTime - 130000); // Restart the cycle with updated remaining time
            }, 60000); // 60 seconds of no activity

        }, Math.min(60000, remainingTime - 10000)); // 1 minute of medium activity or remaining time
    }, Math.min(10000, remainingTime)); // 10 seconds of high activity or remaining time
};

const uploadAndStartCycle = async (bucketName, filePath) => {
    const baseKey = path.basename(filePath);
    const uploadParams = {
        Bucket: bucketName,
        Key: baseKey,
        Body: fs.createReadStream(filePath),
    };

    try {
        const upload = new Upload({ client: s3, params: uploadParams });
        await upload.done();

        // Clear line and log message
        process.stdout.clearLine();
        process.stdout.cursorTo(0);
        console.log(`Uploaded ${baseKey} to ${bucketName}`);

        // Start the progress bar based on elapsed time
        progressBar.start(totalDuration, 0);

        // Update progress bar periodically based on time elapsed
        const startTime = Date.now();
        const progressInterval = setInterval(() => {
            const elapsedTime = Date.now() - startTime;
            progressBar.update(elapsedTime);

            if (elapsedTime >= totalDuration) {
                clearInterval(progressInterval);
                clearInterval(copyInterval);
                progressBar.stop();
                
                // Clear line and log final message
                process.stdout.clearLine();
                process.stdout.cursorTo(0);
                console.log('Test duration of 30 minutes completed. Stopping.');
            }
        }, progressUpdateInterval);

        // Start the cyclical activity pattern
        runActivityCycle(bucketName, baseKey, totalDuration);

    } catch (error) {
        process.stdout.clearLine();
        process.stdout.cursorTo(0);
        console.error('Error during upload or copy:', error.message);
    }
};

const getVideoFilePath = async () => {
    const videoPath = path.join(__dirname, 'video');
    try {
        const files = await fsPromises.readdir(videoPath);
        const videoFiles = files.filter(file => /\.(mp4|mov|avi|mkv)$/i.test(file));

        if (videoFiles.length !== 1) {
            throw new Error('There should be exactly one video file in the ./video directory.');
        }

        return path.join(videoPath, videoFiles[0]);
    } catch (error) {
        throw new Error(`Error reading video directory: ${error.message}`);
    }
};

const promptUserInput = () => {
    rl.question('Enter the S3 bucket name: ', async (bucketName) => {
        rl.question('Enter the AWS region (default: us-east-1): ', async (region) => {
            // Default to 'us-east-1' if no region is provided
            const awsRegion = region.trim() || 'us-east-1';
            s3 = new S3Client({ region: awsRegion }); // Initialize S3 client with the specified region
            
            try {
                const filePath = await getVideoFilePath();

                // Print the test duration
                console.log(`[${new Date().toLocaleTimeString()}] Starting the test for 30 minutes...`);

                await uploadAndStartCycle(bucketName, filePath);
            } catch (error) {
                console.error(error.message);
            } finally {
                rl.close();
            }
        });
    });
};

// Handle interruption (Ctrl+C)
process.on('SIGINT', () => {
    console.log('Interrupted. Stopping the copy process.');
    clearInterval(copyInterval);
    progressBar.stop();
    rl.close();
    process.exit();
});

// Start the user input prompt
promptUserInput();
