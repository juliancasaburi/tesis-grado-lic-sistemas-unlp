# Setup and deployment

## Prerequisites

- **AWS Account**: Ensure you have an AWS account with permissions to create and manage DynamoDB resources.
- **AWS CLI**: [Install](https://aws.amazon.com/cli/) and configure the AWS CLI if you want to create the table via CLI commands.
- **Node.js**: [Install Node.js](https://nodejs.org/) (v20 or later) if it is not already installed.
- **AWS SDK for JavaScript (v3)**: This project uses the AWS SDK v3 to interact with DynamoDB.
- **Kubernetes Cluster**: A Kubernetes cluster must be set up and accessible via `kubectl`.
- **OpenFaaS CLI**: [Install the OpenFaaS CLI](https://docs.openfaas.com/cli/install/).

## Deploying the Application

Execute the `deploy.sh` script:

```bash
./deploy.sh
```

## Troubleshooting

- **AWS Credentials**: If you get an access error, ensure that your AWS credentials are properly configured. You can configure them using:

  ```bash
  aws configure
  ```
