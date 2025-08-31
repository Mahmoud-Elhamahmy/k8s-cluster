variable "aws_region" {
  default = "us-east-1"
}
variable "master_instance_type" {
  default = "t3.medium"
}
variable "worker_instance_type" {
  default = "t3.medium"
}
variable "worker_count" {
  default = 2
}
variable "allowed_api_ips" {
  default = ["0.0.0.0/0"]
  description = "CIDR blocks allowed to access Kubernetes API server"
}
variable "ssh_public_key" {
  type        = string
  description = "SSH public key for EC2 instances"
}

variable "ubuntu_ami" {
  description = "Ubuntu 22.04 AMI ID for your region"
  default     = "ami-0bbdd8c17ed981ef9"
}
