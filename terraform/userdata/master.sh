#!/bin/bash
set -ex

apt-get update -y
apt-get install -y docker.io apt-transport-https curl gnupg lsb-release

# Install Kubernetes
mkdir -p /etc/apt/keyrings
curl -fsSLo /etc/apt/keyrings/kubernetes-archive-keyring.gpg https://dl.k8s.io/apt/doc/apt-key.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list

apt-get update -y
apt-get install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl

# Initialize cluster
kubeadm init --pod-network-cidr=10.244.0.0/16

# Wait until admin.conf exists
until [ -f /etc/kubernetes/admin.conf ]; do
  echo "Waiting for kubeadm to finish..."
  sleep 5
done

# Setup kubeconfig for ubuntu user
mkdir -p /home/ubuntu/.kube
cp -i /etc/kubernetes/admin.conf /home/ubuntu/.kube/config
chown ubuntu:ubuntu /home/ubuntu/.kube/config

# Install a Pod network (Flannel)
sudo -u ubuntu kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml

# Save join command for workers
kubeadm token create --print-join-command > /home/ubuntu/join.sh
chmod +x /home/ubuntu/join.sh
