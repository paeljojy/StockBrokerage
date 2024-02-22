```bash

# Start kube
minikube start

# List external ip
kubectl get svc

# List pods
kubectl get pods

# Init pods
# TODO:
# kubectl apply 

# Pods cluster info
kubectl describe pods

# Create tunnel
minikube tunnel

# Start pods
kubectl apply -f kubernetes/Kube.yaml

# Docker env
eval $(minikube docker-env)

# Build docker compose
docker-compose -f docker-compose.yml build

# Create kubernetes deployment
kubectl create deployment stock-brokerage1
kubectl create deployment my-deployment --image=my-local-image:tag

kubectl create deployment stock-brokerage1 --image=stock-brokerage-server:latest
kubectl create deployment stock-brokerage2 --image=stock-brokerage-client:latest

# Expose ports
kubectl expose deployment stock-brokerage1 --type=LoadBalancer --port=5173
kubectl expose deployment stock-brokerage2 --type=LoadBalancer --port=5000

# Update patch deployment policy
kubectl patch deployment stock-brokerage1 -p '{"spec": {"template": {"spec": {"containers": [{"name": "stock-brokerage-server", "imagePullPolicy": "IfNotPresent"}]}}}}'
kubectl patch deployment stock-brokerage2 -p '{"spec": {"template": {"spec": {"containers": [{"name": "stock-brokerage-client", "imagePullPolicy": "IfNotPresent"}]}}}}'

# Delete deployment
kubectl delete -n default deployment hello-minikube

# Delete pods
kubectl delete pod pod-name

# Logs and events INFO: check --help for more options
kubectl logs pod-name
kubectl get events

```

