#!/bin/bash
set -ex

apt-get update -y
apt-get install -y docker.io apt-transport-https curl gnupg lsb-release

# Install Kubernetes
mkdir -p /etc/apt/keyrings
curl -fsSLo /etc/apt/keyrings/kubernetes-archive-keyring.gpg https://dl.k8s.io/apt/doc/apt-key.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list

apt-get update -y
apt-get install -y kubelet kubeadm
apt-mark hold kubelet kubeadm

# Join cluster if join.sh exists
if [ -f /tmp/join.sh ]; then
  bash /tmp/join.sh
fi
