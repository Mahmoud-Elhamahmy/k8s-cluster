#!/bin/bash
set -ex

# Install dependencies
apt-get update -y
apt-get install -y docker.io apt-transport-https curl gnupg lsb-release

# Add Kubernetes GPG key
mkdir -p /etc/apt/keyrings
curl -fsSLo /etc/apt/keyrings/kubernetes-archive-keyring.gpg https://dl.k8s.io/apt/doc/apt-key.gpg

# Add Kubernetes apt repo
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] \
https://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list

apt-get update -y
apt-get install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl

# Initialize master
kubeadm init --pod-network-cidr=10.244.0.0/16

# Configure kubectl for ubuntu user
mkdir -p /home/ubuntu/.kube
cp -i /etc/kubernetes/admin.conf /home/ubuntu/.kube/config
chown ubuntu:ubuntu /home/ubuntu/.kube/config

# Install flannel CNI
su - ubuntu -c "kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml"

# Allow master to schedule pods
su - ubuntu -c "kubectl taint nodes --all node-role.kubernetes.io/master- || true"

# Save join command
kubeadm token create --print-join-command > /home/ubuntu/join.sh
chmod +x /home/ubuntu/join.sh
chown ubuntu:ubuntu /home/ubuntu/join.sh
