# outputs.tf

output "api_endpoint" {
  description = "The URL of the deployed API Gateway"
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "dynamodb_table_name" {
  description = "The name of the DynamoDB table"
  value       = aws_dynamodb_table.main_table.name
}

output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "The IDs of the public subnets"
  value       = [for subnet in aws_subnet.public : subnet.id]
}

output "cognito_user_pool_id" {
  description = "The ID of the Cognito User Pool"
  value       = aws_cognito_user_pool.main.id
}

output "cognito_app_client_id" {
  description = "The ID of the Cognito App Client"
  value       = aws_cognito_user_pool_client.app_client.id
}

output "original_videos_bucket_name" {
  description = "The name of the S3 bucket for original videos"
  value       = aws_s3_bucket.original_videos.bucket
}

output "transcoded_videos_bucket_name" {
  description = "The name of the S3 bucket for transcoded videos"
  value       = aws_s3_bucket.transcoded_videos.bucket
}
