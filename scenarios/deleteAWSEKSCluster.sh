#!/bin/bash

# Get the current Kubernetes context (which usually contains the cluster name)
CURRENT_CONTEXT=$(kubectl config view --minify -o jsonpath='{.clusters[].name}')

# Display the current Kubernetes context
echo "The current Kubernetes context (cluster) is: $CURRENT_CONTEXT"

# Define the EKS cluster name and region
CLUSTER_NAME="tesina-casaburi"
REGION="sa-east-1"

# Ask for confirmation
while true; do
  read -p "WARNING: This action will permanently delete the EKS cluster '$CLUSTER_NAME' and all services. Are you sure you want to proceed? (yes/no): " confirmation
  case $confirmation in
    [Yy]* ) break;;  # Continue if user confirms
    [Nn]* ) echo "Aborting deletion."; exit 0;;  # Exit if user declines
    * ) echo "Please answer 'yes' or 'no'.";;  # Prompt for valid input
  esac
done

# Delete all services in all namespaces
echo "Deleting all services in the cluster..."
kubectl delete svc --all --all-namespaces

# Check if the deletion of services was successful
if [ $? -ne 0 ]; then
  echo "Failed to delete one or more services"
  exit 1
fi

# Delete the EKS cluster
echo "Deleting the EKS cluster..."
eksctl delete cluster --name "$CLUSTER_NAME" --region "$REGION"

# Check if the cluster was deleted successfully
if [ $? -ne 0 ]; then
  echo "Failed to delete the EKS cluster"
  exit 1
fi

echo "All services and the EKS cluster deleted successfully."
