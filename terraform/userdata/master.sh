#!/bin/bash
set -ex

# Install dependencies
apt-get update -y
apt-get install -y docker.io apt-transport-https curl

# Install Kubernetes
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list
apt-get update -y
apt-get install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl

# Initialize Kubernetes
kubeadm init --pod-network-cidr=10.244.0.0/16

# Copy kubeconfig for ubuntu user
mkdir -p /home/ubuntu/.kube
cp -i /etc/kubernetes/admin.conf /home/ubuntu/.kube/config
chown -R ubuntu:ubuntu /home/ubuntu/.kube

# Wait for control plane to be ready
sleep 30

# Apply Flannel CNI as ubuntu
sudo -u ubuntu kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

# Allow master scheduling
sudo -u ubuntu kubectl taint nodes --all node-role.kubernetes.io/master- || true

# Save join command
kubeadm token create --print-join-command > /home/ubuntu/join.sh
chown ubuntu:ubuntu /home/ubuntu/join.sh
