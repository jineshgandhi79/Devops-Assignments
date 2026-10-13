terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
  }

  backend "s3" {
    bucket         = "devops-enterprise-tf-state-prod"
    key            = "session21/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "devops-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "DevOps-Final-Project"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "Jinesh Gandhi"
    }
  }
}

# Module: VPC Infrastructure
module "vpc" {
  source              = "./modules/vpc"
  environment         = var.environment
  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs= var.private_subnet_cidrs
}

# Module: EKS Cluster Infrastructure
module "eks" {
  source          = "./modules/eks"
  cluster_name    = "devops-production-cluster"
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets
  instance_types  = ["t3.medium"]
  desired_capacity= 3
  max_capacity    = 6
  min_capacity    = 2
}
