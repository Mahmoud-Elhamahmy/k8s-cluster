markdown name=README.md
# Automated Kubernetes Cluster & Juice Shop Deployment (AWS, Terraform, GitHub Actions)

## Overview

This repository provisions a self-managed Kubernetes cluster (not EKS/GKE) on AWS EC2 using Terraform, restricts API access to specific IPs, and deploys Juice Shop via GitHub Actions.

**Features:**
- Automated infrastructure provisioning using Terraform
- API server access restricted to your IP
- K8s setup with kubeadm (master + workers)
- NGINX Ingress Controller
- Juice Shop deployment, service, and ingress
- GitHub Actions for continuous delivery

## Prerequisites

- AWS account and user with EC2 permissions
- SSH key pair in AWS (`key_name`)
- Your public IP address
- GitHub repository secrets:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `SSH_PRIVATE_KEY` (private key for accessing EC2 instances)
- Replace the Ubuntu AMI ID in `main.tf` with a valid one for your region.

## Usage

1. Fork/clone this repository.
2. Edit `terraform/variables.tf`:
    - Set your public IP in `allowed_api_ips`
    - Set your SSH key name in `key_name`
3. Set GitHub secrets as above.
4. Push changes to `main`—GitHub Actions will provision infrastructure and deploy manifests.

## Monitoring Recommendations

- **Prometheus Operator & Grafana**: Cluster/app metrics and dashboards
- **Node Exporter**: VM metrics
- **EFK/ELK Stack**: Log aggregation/search
- **Kube-state-metrics**: Cluster state
- **NGINX Metrics**: Ingress monitoring
- **Falco**: Runtime security monitoring

## Directory Structure

```
.
├── .github/
│   └── workflows/
│       └── terraform.yml
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── providers.tf
│   ├── security.tf
│   ├── user_data_master.sh
│   └── user_data_worker.sh
├── manifests/
│   ├── juice-shop-deployment.yaml
│   ├── juice-shop-service.yaml
│   └── juice-shop-ingress.yaml
```
