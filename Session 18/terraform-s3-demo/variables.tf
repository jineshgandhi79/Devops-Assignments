variable "aws_region" {
  type        = string
  description = "AWS region for the S3 bucket deployment"
  default     = "us-east-1"
}

variable "bucket_name" {
  type        = string
  description = "Name tag / prefix identifier for the S3 bucket"
  default     = "jinesh-gandhi-devops-s3-demo-bucket"
}

variable "environment" {
  type        = string
  description = "Deployment environment (e.g., dev, staging, prod)"
  default     = "dev"
}

variable "owner" {
  type        = string
  description = "Author and owner of the infrastructure resources"
  default     = "Jinesh Gandhi"
}
