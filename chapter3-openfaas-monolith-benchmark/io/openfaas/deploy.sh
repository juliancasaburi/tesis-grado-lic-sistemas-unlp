#!/bin/bash

export KUBECONFIG=~/.kube/eksctl/clusters/openfaas-eks

kubectl apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml

PASSWORD=$(head -c 12 /dev/urandom | shasum | cut -d' ' -f1)

kubectl -n openfaas create secret generic basic-auth \
--from-literal=basic-auth-user=admin \
--from-literal=basic-auth-password=$PASSWORD

helm repo add openfaas https://openfaas.github.io/faas-netes/

helm upgrade openfaas --install openfaas/openfaas \
    --namespace openfaas  \
    --set functionNamespace=openfaas-fn \
    --set serviceType=LoadBalancer \
    --set basic_auth=true \
    --set operator.create=true \
    --set gateway.replicas=2 \
    --set queueWorker.replicas=2

sleep 300

export OPENFAAS_URL=$(kubectl get svc -n openfaas gateway-external -o  jsonpath='{.status.loadBalancer.ingress[*].hostname}'):8080  \
&& echo Your gateway URL is: $OPENFAAS_URL

echo $PASSWORD | faas-cli login --username admin --password-stdin

faas-cli deploy -f tesina-scenario-network.yml

# Create secrets
faas-cli secret create dynamodb-access-key-id --from-file=./DYNAMODB_ACCESS_KEY_ID.txt
faas-cli secret create dynamodb-secret-access-key --from-file=./DYNAMODB_SECRET_ACCESS_KEY.txt