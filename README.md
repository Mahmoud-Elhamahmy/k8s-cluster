# Fully Automated Kubernetes Cluster & Juice Shop on AWS (Terraform + GitHub Actions)

## Overview

This repository provisions a **self-managed Kubernetes cluster** (no EKS/GKE) on AWS using **Terraform**, with all necessary networking (VPC, subnet, security groups), EC2 instances, and automated worker joining via SSM.  
Juice Shop, NGINX Ingress, and all manifests are deployed automatically via **GitHub Actions**.

## Features

- **Infrastructure as Code:** All resources (VPC, subnet, IGW, route tables, security groups, EC2 master/worker nodes, IAM roles) are defined in Terraform in a single file (`main.tf`).
- **Network Isolation:** Dedicated VPC, public subnet, managed security groups.
- **Automated Kubernetes Bootstrap:** Master node initializes, creates a join command, and stores it in AWS SSM Parameter Store; workers fetch and join cluster automatically.
- **CI/CD:** GitHub Actions deploys all manifests (Juice Shop, Service, Ingress) after provisioning.
- **API Server Restriction:** API server (`6443`) exposed only to your specified public IP.
- **Public Access:** NGINX Ingress and Juice Shop are accessible via public IP.
- **Destroy Workflow:** Run the `destroy.yml` workflow to clean up all AWS resources using a Python/Boto3 script.

## Usage

1. **Configure Secrets:**
   - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (GitHub secrets)
   - `SSH_PRIVATE_KEY` (GitHub secret, matches key used in `key_name`)
2. **Edit `variables.tf`:**
   - Set your public IP in `allowed_api_ips`
   - Set your SSH key name and Ubuntu AMI (`ubuntu_ami`) for your region
3. **Push to `main` branch:** GitHub Actions provisions infra, joins workers, deploys manifests.
4. **Destroy resources:**  
   On the GitHub Actions tab, run the **"AWS Destroy All Resources"** workflow (`destroy.yml`). It removes EC2, EKS, S3, DynamoDB, RDS, Lambda, SQS, SNS, CloudFormation, Secrets Manager, and related security groups.

## File Structure

```
.
├── main.tf                # All Terraform resources (network, compute, IAM, security)
├── variables.tf           # Terraform variables
├── user_data_master.sh    # Kubernetes master bootstrap (writes join command to SSM)
├── user_data_worker.sh    # Worker bootstrap (fetches join command from SSM)
├── juice-shop-deployment.yaml
├── juice-shop-service.yaml
├── juice-shop-ingress.yaml
├── .github/
│   └── workflows/
│       ├── terraform.yml  # Automated provisioning & deployment
│       └── destroy.yml    # Full AWS cleanup
├── destroy_all.py         # Python script for full AWS account cleanup
```

## Monitoring Recommendations

- Prometheus Operator & Grafana
- Node Exporter
- EFK/ELK Stack
- Kube-state-metrics
- NGINX Metrics
- Falco

## DNS/SSL

- Ingress uses `juice-shop.local`. For public traffic, set up a real domain and update the ingress manifest. For TLS, integrate cert-manager or manually add SSL keys.

## Notes

- **Replace** all placeholder values in `variables.tf` with your own.
- **Make sure** your key in AWS matches `key_name` and secret in GitHub.
- **The destroy script** does a broad sweep—double-check before use in production environments.

```
To destroy all AWS resources, run the "AWS Destroy All Resources" workflow from the Actions tab.
```
