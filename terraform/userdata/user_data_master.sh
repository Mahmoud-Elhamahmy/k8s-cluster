#!/bin/bash
set -e
sudo apt-get update
sudo apt-get install -y docker.io apt-transport-https curl jq awscli
sudo systemctl enable docker
sudo systemctl start docker

# Install kubeadm, kubelet, kubectl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl

# Initialize Kubernetes master
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --ignore-preflight-errors=all

mkdir -p /home/ubuntu/.kube
sudo cp /etc/kubernetes/admin.conf /home/ubuntu/.kube/config
sudo chown ubuntu:ubuntu /home/ubuntu/.kube/config

# Flannel Network
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

# Install ingress-nginx
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/cloud/deploy.yaml

# Generate join command and put in SSM Parameter Store
JOIN_CMD=$(sudo kubeadm token create --print-join-command)
aws ssm put-parameter --name "/k8s/join-command" --type "String" --value "$JOIN_CMD" --overwrite --region ${AWS_REGION:-us-east-1}

# Place manifests for juice shop
cat > /home/ubuntu/juice-shop-deployment.yaml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: juice-shop
spec:
  replicas: 1
  selector:
    matchLabels:
      app: juice-shop
  template:
    metadata:
      labels:
        app: juice-shop
    spec:
      containers:
      - name: juice-shop
        image: bkimminich/juice-shop
        ports:
        - containerPort: 3000
EOF

cat > /home/ubuntu/juice-shop-service.yaml <<EOF
apiVersion: v1
kind: Service
metadata:
  name: juice-shop
spec:
  selector:
    app: juice-shop
  ports:
    - protocol: TCP
      port: 3000
      targetPort: 3000
EOF

cat > /home/ubuntu/juice-shop-ingress.yaml <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: juice-shop-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: juice-shop.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: juice-shop
            port:
              number: 3000
EOF
