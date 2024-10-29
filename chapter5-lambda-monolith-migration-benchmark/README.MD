# Deploying CloudFormation Stacks
This guide provides instructions for deploying CloudFormation stacks for both Lambda-based and monolithic architectures, as well as an EC2 instance used for load testing with K6.

## Prerequisites
Before you begin, make sure the following requirements are met:

1. AWS CLI is installed and configured with the appropriate credentials.
2. You have IAM permissions to create and manage the required AWS resources (e.g., EC2, Lambda, API Gateway, IAM roles, etc.).
3. AWS SAM CLI is installed.

## Directory Structure

Each application has two subdirectories:

1. `lambda/`: Contains the SAM template for the Lambda-based architecture.
2. `monolithic/`: Contains the CloudFormation template for the monolithic architecture.

## Deploying the Lambda Application

To deploy the Lambda-based application, navigate to the lambda/ directory and run the following command:

```bash
sam build && sam deploy --guided --capabilities CAPABILITY_NAMED_IAM
```

This command will build the application and guide you through the deployment process, allowing you to specify your stack name, region, and other parameters.

## Deploying the Monolithic Application
To deploy the monolithic application, navigate to the monolithic/ directory and run the following command:

```bash
aws cloudformation create-stack --stack-name tesina-app-architecture --template-body file://cloudformation-template.yaml --capabilities CAPABILITY_IAM --region us-east-1
```

Replace `tesina-app-architecture` with your preferred stack name.

## Deploying the EC2 Test Instance
In the root directory of each application, you'll also find the `cloudformation-ec2-test-machine.yaml`template. This CloudFormation template is for deploying an EC2 instance that can be used for load testing both the Lambda and monolithic applications using K6.

To deploy the EC2 instance, use the following command:

```bash
aws cloudformation create-stack --stack-name tesina-test-instance --template-body file://cloudformation-ec2-test-machine.yaml --capabilities CAPABILITY_IAM --region us-east-1
```

### Notes
- Ensure the stack names are unique within your AWS account to avoid conflicts.

# Deleting a SAM Application
To delete a SAM application, you can use the `sam delete` command. This command simplifies the process by automatically deleting the CloudFormation stack associated with your SAM deployment.

```bash
sam delete --stack-name <stack-name> --region us-east-1
```


# Deleting CloudFormation Stacks

1. List All Active Stacks

    Before deleting, you can list your active stacks to identify which ones to remove:

    ```bash
    aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --region us-east-1
    ```

2. Delete the Stacks

    To delete a specific stack, use the following command:

    ```bash
    aws cloudformation delete-stack --stack-name <stack-name> --region us-east-1
    ```

    Replace `<stack-name>` with the actual name of the stack you deployed (e.g., `tesina-app-lambda` or `tesina-test-instance`).

    Repeat this process for all the stacks you wish to remove.

3. Check Deletion Status

    You can check the progress of the deletion using:

    ```bash
    aws cloudformation describe-stacks --stack-name <stack-name> --region us-east-1
    ```

    The status will transition to `DELETE_IN_PROGRESS` and eventually to `DELETE_COMPLETE` once it has finished.