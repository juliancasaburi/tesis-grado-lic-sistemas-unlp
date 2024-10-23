#!/bin/bash

faas-cli rm -f tesina-scenario-network.yml

# Remove secret
# faas-cli secret remove dynamodb

# Delete all resources OpenFaaS namespaces
kubectl delete all --all -n openfaas
kubectl delete all --all -n openfaas-fn
kubectl delete role --all -n openfaas
kubectl delete rolebinding --all -n openfaas
kubectl delete role --all -n openfaas-fn
kubectl delete rolebinding --all -n openfaas-fn