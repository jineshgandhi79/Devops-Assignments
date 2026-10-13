variable "aws_region" {
  description = "The AWS region where resources will be provisioned"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Prefix for all resource naming conventions"
  type        = string
  default     = "cloud-infra-demo"
}

variable "environment" {
  description = "Deployment environment (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the custom VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "availability_zone" {
  description = "Availability zone for subnet placement"
  type        = string
  default     = "us-east-1a"
}

variable "instance_type" {
  description = "EC2 instance hardware specification"
  type        = string
  default     = "t2.micro"
}

variable "s3_bucket_prefix" {
  description = "Prefix identifier for the S3 bucket"
  type        = string
  default     = "cloud-infra-assets"
}
