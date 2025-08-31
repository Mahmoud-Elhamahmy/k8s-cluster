#!/bin/bash
set -e
sudo apt-get update
sudo apt-get install -y docker.io apt-transport-https curl
sudo systemctl enable docker
sudo systemctl start docker

# Install kubeadm, kubelet, kubectl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl

# The join command will be run automatically by GitHub Actions after provisioning
# See .github/workflows/terraform.yml for automation
