# Deploying CloudFormation Stacks
This guide provides instructions for deploying CloudFormation stacks for both Lambda-based and monolithic architectures, as well as an EC2 instance used for load testing with K6.

## Prerequisites
Before you begin, make sure the following requirements are met:

1. AWS CLI is installed and configured with the appropriate credentials.
2. You have IAM permissions to create and manage the required AWS resources (e.g., EC2, Lambda, API Gateway, IAM roles, etc.).

## Directory Structure

Each application has two subdirectories:

1. `lambda/`: Contains the CloudFormation template for the Lambda-based architecture.
2. `monolithic/`: Contains the CloudFormation template for the monolithic architecture.

Each subdirectory includes a `cloudformation-template.yaml` file for deploying the respective architecture.

## Deploying Lambda and Monolithic Stacks

To deploy either the Lambda or monolithic architecture, navigate to the corresponding directory and run the following command:

```bash
aws cloudformation create-stack --stack-name tesina-app-architecture --template-body file://cloudformation-template.yaml --capabilities CAPABILITY_IAM --region us-east-1
```

Replace tesina-app-architecture with your preferred stack name.

## Deploying the EC2 Test Instance
In the root directory of each application, you'll also find the `cloudformation-ec2-test-machine.yaml`template. This CloudFormation template is for deploying an EC2 instance that can be used for load testing both the Lambda and monolithic applications using K6.

To deploy the EC2 instance, use the following command:

```bash
aws cloudformation create-stack --stack-name tesina-test-instance --template-body file://cloudformation-ec2-test-machine.yaml --capabilities CAPABILITY_IAM --region us-east-1
```

### Notes
- Ensure the stack names are unique within your AWS account to avoid conflicts.

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