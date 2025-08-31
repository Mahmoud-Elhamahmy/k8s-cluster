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

# Wait for master to create join command
while ! aws ssm get-parameter --name "/k8s/join-command" --region ${AWS_REGION:-us-east-1} --query 'Parameter.Value' --output text; do
  sleep 10
done

JOIN_CMD=$(aws ssm get-parameter --name "/k8s/join-command" --region ${AWS_REGION:-us-east-1} --query 'Parameter.Value' --output text)
sudo $JOIN_CMD
