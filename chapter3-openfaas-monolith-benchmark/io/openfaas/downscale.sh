#!/bin/bash

faas-cli rm -f tesina-scenario-network.yml

# Remove secrets
faas-cli secret remove dynamodb-access-key-id
faas-cli secret remove dynamodb-secret-access-key

# Delete all resources OpenFaaS namespaces
kubectl delete all --all -n openfaas
kubectl delete all --all -n openfaas-fn
kubectl delete role --all -n openfaas
kubectl delete rolebinding --all -n openfaas
kubectl delete role --all -n openfaas-fn
kubectl delete rolebinding --all -n openfaas-fn