provider "aws" { region = var.region }


resource "aws_key_pair" "k8s" {
  key_name   = "k8s-key"
  public_key = var.ssh_public_key
}
############################
# AWS VPC, Subnet, Network #
############################

resource "aws_vpc" "k8s_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "k8s-vpc" }
}

resource "aws_internet_gateway" "k8s_igw" {
  vpc_id = aws_vpc.k8s_vpc.id
  tags = { Name = "k8s-igw" }
}

resource "aws_subnet" "k8s_public_subnet" {
  vpc_id                  = aws_vpc.k8s_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"
  tags = { Name = "k8s-public-subnet" }
}

resource "aws_route_table" "k8s_public_rt" {
  vpc_id = aws_vpc.k8s_vpc.id
  tags = { Name = "k8s-public-rt" }
}

resource "aws_route" "default_route" {
  route_table_id         = aws_route_table.k8s_public_rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.k8s_igw.id
}

resource "aws_route_table_association" "k8s_public_rt_assoc" {
  subnet_id      = aws_subnet.k8s_public_subnet.id
  route_table_id = aws_route_table.k8s_public_rt.id
}

############################
# Security Group           #
############################

resource "aws_security_group" "k8s" {
  name        = "k8s-cluster-sg"
  description = "K8s cluster security group"
  vpc_id      = aws_vpc.k8s_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = var.allowed_api_ips
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

############################
# IAM Role for SSM         #
############################

resource "aws_iam_role" "ssm_role" {
  name = "k8s-ssm-role"
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "ec2.amazonaws.com"
        },
        "Effect": "Allow"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_attach" {
  role       = aws_iam_role.ssm_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ssm_profile" {
  name = "k8s-ssm-profile"
  role = aws_iam_role.ssm_role.name
}

############################
# EC2 Instances            #
############################

resource "aws_instance" "master" {
  ami                         = var.ubuntu_ami
  instance_type               = var.master_instance_type
  key_name                    = aws_key_pair.k8s.key_name
  subnet_id                   = aws_subnet.k8s_public_subnet.id
  associate_public_ip_address = true
  security_groups             = [aws_security_group.k8s.id]
  iam_instance_profile        = aws_iam_instance_profile.ssm_profile.name
  user_data                   = file("${path.module}/user_data_master.sh")
  tags = { Name = "k8s-master" }
}

resource "aws_instance" "worker" {
  count                       = var.worker_count
  ami                         = var.ubuntu_ami
  instance_type               = var.worker_instance_type
  key_name                    = aws_key_pair.k8s.key_name
  subnet_id                   = aws_subnet.k8s_public_subnet.id
  associate_public_ip_address = true
  security_groups             = [aws_security_group.k8s.id]
  iam_instance_profile        = aws_iam_instance_profile.ssm_profile.name
  user_data                   = file("${path.module}/user_data_worker.sh")
  tags = { Name = "k8s-worker-${count.index}" }
}
