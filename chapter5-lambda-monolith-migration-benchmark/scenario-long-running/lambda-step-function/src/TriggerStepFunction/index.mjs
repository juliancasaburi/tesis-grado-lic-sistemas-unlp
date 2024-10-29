import { SFNClient, StartExecutionCommand } from "@aws-sdk/client-sfn";

const sfnClient = new SFNClient();

export const handler = async (event) => {
  const srcBucket = event.Records[0].s3.bucket.name;
  const srcKey = decodeURIComponent(event.Records[0].s3.object.key.replace(/\+/g, ' '));

  const stepFunctionArn = process.env.STEP_FUNCTION_ARN;

  const input = JSON.stringify({
    bucket: srcBucket,
    key: srcKey,
  });

  try {
    await sfnClient.send(new StartExecutionCommand({
      stateMachineArn: stepFunctionArn,
      input: input
    }));

    console.log(`Step function triggered for video: ${srcKey}`);
    return { statusCode: 200, body: 'Step function started' };

  } catch (err) {
    console.error("Error starting Step Function:", err);
    throw new Error("Step Function failed to start.");
  }
};
