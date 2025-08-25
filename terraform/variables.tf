variable "region" { default = "us-east-1" }
variable "master_type" { default = "t3.medium" }
variable "worker_type" { default = "t3.medium" }
variable "worker_count" { default = 1 }
variable "ssh_key_name" {
  description = "AWS key pair name"
  default     = "my-key"
}
variable "my_ip" {
  description = "Restrict access to your IP"
  default     = "197.52.44.177/32"
}
variable "ami_id" {
  description = "Ubuntu 22.04 AMI"
  default     = "ami-0bbdd8c17ed981ef9"
}
