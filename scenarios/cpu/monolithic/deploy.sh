#!/bin/bash

kubectl apply -f service.yml -f deployment.yml -n monolithic

kubectl -n monolithic patch svc tesina-scenario-cpu-monolithic-service -p '{"spec": {"type": "LoadBalancer"}}'