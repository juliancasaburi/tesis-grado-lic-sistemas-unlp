# Creating the cluster
# EKS Cluster Setup
Sets up an Amazon EKS cluster using eksctl and configures namespaces and monitoring with the kube-prometheus-stack Helm chart.

## Prerequisites
Before running the script, ensure you have the following tools installed and configured:

### 1. AWS CLI
The AWS CLI is needed to interact with AWS services. Follow the official [documentation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) to install and configure it.

```bash
aws configure
```

Ensure that you have the correct IAM permissions to create EKS clusters and the necessary resources.

### 2. eksctl
eksctl is a simple CLI tool to create and manage EKS clusters.

[Installation guide for eksctl](https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html)

### 3. kubectl

[Installation guide for kubectl](https://kubernetes.io/docs/tasks/tools/)

### 4. Helm

Helm is a package manager for Kubernetes.

[Installation guide for Helm](https://helm.sh/docs/intro/install/)

## How to create the cluster
Run the provided [Bash script](./createAWSEKSCluster.sh) to create the cluster, namespaces, and install the monitoring stack.

# Local Kubernetes Cluster Setup with kind
Sets up a cluster using kind and configures namespaces and monitoring with the kube-prometheus-stack Helm chart.

## Prerequisites
Before running the script, ensure you have the following tools installed and configured:

### 1. Docker
kind requires Docker to run Kubernetes nodes as containers. Ensure Docker is installed and running.

[Installation guide for docker engine](https://docs.docker.com/engine/install/)

Ensure that you have the correct IAM permissions to create EKS clusters and the necessary resources.

### 2. kind
kind is a tool for running local Kubernetes clusters using Docker containers.

[Installation guide for kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

### 3. kubectl

[Installation guide for kubectl](https://kubernetes.io/docs/tasks/tools/)

### 4. Helm

Helm is a package manager for Kubernetes.

[Installation guide for Helm](https://helm.sh/docs/intro/install/)

## How to create the cluster
Ensure Docker is running and run the provided [Bash script](./createLocalCluster.sh) to create the cluster, namespaces, and install the monitoring stack.