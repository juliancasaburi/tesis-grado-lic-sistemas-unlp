#!/bin/bash

eksctl create cluster --name=tesina-casaburi --nodes=1 --auto-kubeconfig --region=sa-east-1

# Check if the cluster was created successfully
if [ $? -ne 0 ]; then
  echo "Failed to create the Kubernetes cluster"
  exit 1
fi

# Create the 'monolithic' namespace
kubectl create namespace monolithic

# Check if the namespace was created successfully
if [ $? -ne 0 ]; then
  echo "Failed to create namespace 'monolithic'"
  exit 1
fi

# Create the 'monitoring' namespace
kubectl create namespace monitoring

# Check if the namespace was created successfully
if [ $? -ne 0 ]; then
  echo "Failed to create namespace 'monitoring'"
  exit 1
fi

# Install the kube-prometheus-stack using Helm in the 'monitoring' namespace
helm install kube-prometheus-stack --create-namespace --namespace monitoring prometheus-community/kube-prometheus-stack

# Check if the Helm installation was successful
if [ $? -ne 0 ]; then
  echo "Failed to install kube-prometheus-stack with Helm"
  exit 1
fi

echo "Kubernetes cluster and monitoring stack setup completed successfully"
