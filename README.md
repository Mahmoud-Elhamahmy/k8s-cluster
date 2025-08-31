# Fully Automated K8s Cluster & Juice Shop on AWS (Terraform + GitHub Actions)

## Overview

- Terraform provisions VPC, subnet, EC2 (master/workers), security groups, SSM, SSH keys
- Master auto-initializes, creates join token, stores join command in SSM parameter
- Workers fetch join command from SSM and join cluster automatically
- NGINX Ingress and Juice Shop automatically deployed via GitHub Actions

## Usage

1. Set AWS credentials as GitHub secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. Set your SSH private key as `SSH_PRIVATE_KEY`
3. Set your public IP in `terraform/variables.tf` (`allowed_api_ips`)
4. Set your SSH key name and Ubuntu AMI in `variables.tf`
5. Push to `main` branch—GitHub Actions provisions infra, joins workers, deploys manifests

## Monitoring Recommendations

- Prometheus Operator & Grafana
- Node Exporter
- EFK/ELK Stack
- Kube-state-metrics
- NGINX Metrics
- Falco

## How Worker Join is Automated

- Master writes the join command to AWS SSM Parameter Store
- Workers fetch the join command in their cloud-init and execute it

## DNS/SSL

- Ingress uses `juice-shop.local`. For public traffic, set up a real domain and update the ingress manifest.
