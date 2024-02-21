```bash

# Start kube
minikube start

# list external ip
kubectl get svc

# list pods
kubectl get pods

# init pods
# TODO:
# kubectl apply 

# pods cluster info
kubectl describe pods

# create tunnel
minikube tunnel

# start pods
kubectl apply -f kubernetes/Kube.yaml

# docker env
eval $(minikube docker-env)

# build docker compose
docker-compose -f docker-compose.yml build

# create kubernetes deployment
kubectl create deployment stock-brokerage1 

kubectl create deployment my-deployment --image=my-local-image:tag

kubectl create deployment stock-brokerage2 --image=stock-brokerage-server:latest

kubectl create deployment stock-brokerage2 --image=stock-brokerage-client:latest

# 
kubectl expose deployment stock-brokerage1 --type=LoadBalancer --port=5173
kubectl expose deployment stock-brokerage2 --type=LoadBalancer --port=5000

kubectl expose deployment stock-brokerage1 --type=LoadBalancer --port=5173
kubectl expose deployment stock-brokerage2 --type=LoadBalancer --port=5000

# update patch deployment policy
kubectl patch deployment stock-brokerage1 -p '{"spec": {"template": {"spec": {"containers": [{"name": "stock-brokerage-server", "imagePullPolicy": "IfNotPresent"}]}}}}'

kubectl patch deployment stock-brokerage2 -p '{"spec": {"template": {"spec": {"containers": [{"name": "stock-brokerage-client", "imagePullPolicy": "IfNotPresent"}]}}}}'

# delete deployment
kubectl delete -n default deployment hello-minikube

```
