output "vpc_id" {
  description = "Created VPC Identifier"
  value       = module.vpc.vpc_id
}

output "eks_cluster_name" {
  description = "EKS Cluster Name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS Cluster API Server Endpoint"
  value       = module.eks.cluster_endpoint
}
