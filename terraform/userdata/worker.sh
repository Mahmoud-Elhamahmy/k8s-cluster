#!/bin/bash
set -ex
apt-get update -y
apt-get install -y docker.io apt-transport-https curl

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list
apt-get update -y
apt-get install -y kubelet kubeadm
apt-mark hold kubelet kubeadm
# Join command must be pulled from master manually or via automation
