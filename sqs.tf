# sqs_ses.tf

# 1. Cola de SQS para notificaciones por email
resource "aws_sqs_queue" "email_notifications" {
  name                      = "${var.project_name}-email-notifications-queue"
  delay_seconds             = 0
  max_message_size          = 262144 # 256 KB
  message_retention_seconds = 86400  # 1 día
  visibility_timeout_seconds = 30

  tags = {
    Name = "${var.project_name}-email-queue"
  }
}
