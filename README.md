# Automated Kubernetes Cluster & Juice Shop Deployment (AWS, Terraform, GitHub Actions)

## Summary

This repository provisions a self-managed Kubernetes cluster (not EKS) on AWS EC2 using Terraform, restricts API access to specific IPs, and deploys Juice Shop via GitHub Actions.

## How It Works

- **Terraform:** Provisions EC2 (1 master, N workers), security groups, SSH keys, and bootstraps K8s with kubeadm.
- **GitHub Actions:** Runs `terraform apply` and deploys Kubernetes manifests over SSH.

## Usage

1. Set AWS credentials as GitHub secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).
2. Set up your public IP in `terraform/variables.tf` for API restriction.
3. Set your SSH key as a GitHub secret (`SSH_PRIVATE_KEY`).
4. Push to main branch; GitHub Actions will provision and deploy everything.

## Monitoring Recommendations

- **Prometheus Operator & Grafana**
- **Node Exporter**
- **EFK/ELK Stack**
- **Kube-state-metrics**
- **NGINX Metrics**
- **Falco**

---
