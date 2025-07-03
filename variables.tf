variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "The name of the project, used for tagging resources."
  type        = string
  default     = "ElearningProject"
}

variable "vpc_cidr_block" {
  description = "The CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "The CIDR blocks for the public subnets."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "The CIDR blocks for the private subnets."
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "availability_zones" {
  description = "The availability zones to deploy the subnets in."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "table_name" {
  description = "The name of the DynamoDB table."
  type        = string
  default     = "ElearningPlatformTable"
}

variable "sender_email" {
  description = "The email address verified in SES to send emails from."
  type        = string
  default     = "proyect2024up@gmail.com" # Reemplazar con tu email verificado
}
