output "bucket_id" {
  description = "The name / ID of the created S3 bucket"
  value       = aws_s3_bucket.demo_bucket.id
}

output "bucket_arn" {
  description = "The Amazon Resource Name (ARN) of the bucket"
  value       = aws_s3_bucket.demo_bucket.arn
}

output "bucket_region" {
  description = "The AWS region where the bucket is hosted"
  value       = aws_s3_bucket.demo_bucket.region
}

output "versioning_status" {
  description = "Versioning configuration status"
  value       = aws_s3_bucket_versioning.demo_bucket_versioning.versioning_configuration[0].status
}
