#!/bin/bash

# Delete the Kubernetes cluster
kind delete cluster --name tesina-casaburi

# Check if the cluster was deleted successfully
if [ $? -ne 0 ]; then
  echo "Failed to delete the Kubernetes cluster"
  exit 1
fi

echo "Kubernetes cluster deleted successfully"
