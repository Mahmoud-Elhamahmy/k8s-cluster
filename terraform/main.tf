provider "aws" { region = var.region }


resource "aws_key_pair" "k8s" {
  key_name   = "k8s-key"
  public_key = var.ssh_public_key
}

# VPC + Subnet + IGW

resource "aws_vpc" "this" {
  cidr_block = "10.0.0.0/16"
}
# Subnet 
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.this.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.this.id
}
resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.this.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}
resource "aws_route_table_association" "rta" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.rt.id
}

# Security group
resource "aws_security_group" "k8s" {
  vpc_id = aws_vpc.this.id

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
    cidr_blocks =["0.0.0.0/0"] # restrict K8s API
  }

  ingress {
    from_port   = 30000
    to_port     = 32767
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

resource "aws_instance" "master" {
  ami           = var.ubuntu_ami
  instance_type = var.master_instance_type
  key_name      = aws_key_pair.deployer.key_name
  security_groups = [aws_security_group.k8s.name]
  iam_instance_profile = aws_iam_instance_profile.ssm_profile.name
  user_data     = file("${path.module}/user_data_master.sh")

  tags = {
    Name = "k8s-master"
  }
}

resource "aws_instance" "worker" {
  count         = var.worker_count
  ami           = var.ubuntu_ami
  instance_type = var.worker_instance_type
  key_name      = aws_key_pair.deployer.key_name
  security_groups = [aws_security_group.k8s.name]
  iam_instance_profile = aws_iam_instance_profile.ssm_profile.name
  user_data     = file("${path.module}/user_data_worker.sh")

  tags = {
    Name = "k8s-worker-${count.index}"
  }
}

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

output "master_public_ip" {
  value = aws_instance.master.public_ip
}
