output "vpc_id" {
  description = "The ID of the custom VPC"
  value       = aws_vpc.main_vpc.id
}

output "subnet_id" {
  description = "The ID of the public subnet"
  value       = aws_subnet.public_subnet.id
}

output "security_group_id" {
  description = "The ID of the web security group"
  value       = aws_security_group.web_sg.id
}

output "ec2_instance_id" {
  description = "The ID of the EC2 instance"
  value       = aws_instance.web_server.id
}

output "ec2_public_ip" {
  description = "Public IP address of the deployed web server"
  value       = aws_instance.web_server.public_ip
}

output "s3_bucket_name" {
  description = "The globally unique name of the S3 bucket"
  value       = aws_s3_bucket.storage_bucket.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.storage_bucket.arn
}
