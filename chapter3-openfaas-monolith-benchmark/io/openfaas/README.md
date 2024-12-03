
# Setup and deployment

This project requires a DynamoDB table named `TesinaNetworkScenarioOpenFaaS` to be created beforehand in on-demand mode and a sample record. Follow the instructions below to set up the table and add the record. Once the DynamoDB setup is complete, you can deploy the application to Kubernetes using the provided deployment script.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Table Requirements](#table-requirements)
- [Setup Instructions](#setup-instructions)
  - [Step 1: Create the DynamoDB Table in On-Demand Mode](#step-1-create-the-dynamodb-table-in-on-demand-mode)
  - [Step 2: Add Initial Record](#step-2-add-initial-record)
  - [Step 3: Verify the Item in DynamoDB](#step-3-verify-the-item-in-dynamodb)
- [Deploying the Application](#deploying-the-application)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **AWS Account**: Ensure you have an AWS account with permissions to create and manage DynamoDB resources.
- **AWS CLI**: [Install](https://aws.amazon.com/cli/) and configure the AWS CLI if you want to create the table via CLI commands.
- **Node.js**: [Install Node.js](https://nodejs.org/) (v20 or later) if it is not already installed.
- **AWS SDK for JavaScript (v3)**: This project uses the AWS SDK v3 to interact with DynamoDB.
- **Kubernetes Cluster**: A Kubernetes cluster must be set up and accessible via `kubectl`.

## Setup Instructions

### Step 1: Create the DynamoDB Table in On-Demand Mode

If the `TesinaNetworkScenarioOpenFaaS` table does not exist, create it manually in the AWS Console or by using the AWS CLI in **on-demand mode**.

**Using AWS CLI:**

```bash
aws dynamodb create-table \
    --table-name TesinaNetworkScenarioOpenFaaS \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

This command creates the `TesinaNetworkScenarioOpenFaaS` table with **on-demand billing**, where you are only charged for the read and write requests you use.

### Step 2: Add Initial Record

To add a sample record to the `TesinaNetworkScenarioOpenFaaS` table, you can use the following steps.

#### 1. Navigate to the aux script directory

```bash
cd ./aux-dynamodb-create-put-record
```

#### 2. Install dependencies

```bash
npm install
```

#### 3. Run the Script

Execute the script by running:

```bash
npm start
```

If the script runs successfully, it will log a message with the `id` and `randomValue` of the inserted record.

### Step 3: Verify the Item in DynamoDB

To confirm that the item was successfully added to your DynamoDB table:

1. Go to the [DynamoDB Console](https://console.aws.amazon.com/dynamodb/).
2. Navigate to **Tables** > `TesinaNetworkScenarioOpenFaaS`.
3. Select **Explore Table** to view the contents of the table and verify that the record with the specified `id` exists.

---

# Deploying the Application

1. Update credentials `DYNAMODB_ACCESS_KEY_ID.txt` and `DYNAMODB_SECRET_ACCESS_KEY.txt`

2. Execute the `deploy.sh` script:

```bash
./deploy.sh
```

## Troubleshooting

- **AWS Credentials**: If you get an access error, ensure that your AWS credentials are properly configured. You can configure them using:

  ```bash
  aws configure
  ```

- **Permissions**: Make sure the AWS credentials used in your environment have sufficient permissions to read and write to DynamoDB.
