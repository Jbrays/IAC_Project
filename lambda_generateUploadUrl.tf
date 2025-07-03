# lambda_generateUploadUrl.tf

# 1. Empaquetado del código fuente
data "archive_file" "generate_upload_url_zip" {
  type        = "zip"
  source_dir  = "logica_recursos/lambdas/generateUploadUrl/"
  output_path = ".terraform/zips/generateUploadUrl.zip"
}

# 2. Rol de IAM
resource "aws_iam_role" "generate_upload_url_lambda_role" {
  name = "${var.project_name}-generateUploadUrl-role"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# 3. Política de IAM (Logs y permiso para PutObject en S3)
resource "aws_iam_policy" "generate_upload_url_lambda_policy" {
  name        = "${var.project_name}-generateUploadUrl-policy"
  description = "IAM policy for generateUploadUrl Lambda"

  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Effect   = "Allow",
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action   = ["s3:PutObject"],
        Effect   = "Allow",
        Resource = "${aws_s3_bucket.original_videos.arn}/*" # Permiso sobre los objetos del bucket
      }
    ]
  })
}

# 4. Adjuntar la política al rol
resource "aws_iam_role_policy_attachment" "generate_upload_url_lambda_attach" {
  role       = aws_iam_role.generate_upload_url_lambda_role.name
  policy_arn = aws_iam_policy.generate_upload_url_lambda_policy.arn
}

# 5. Recurso de la Función Lambda
resource "aws_lambda_function" "generate_upload_url" {
  function_name    = "${var.project_name}-generateUploadUrl"
  handler          = "main.handler"
  runtime          = "python3.9"
  role             = aws_iam_role.generate_upload_url_lambda_role.arn
  filename         = data.archive_file.generate_upload_url_zip.output_path
  source_code_hash = data.archive_file.generate_upload_url_zip.output_base64sha256

  environment {
    variables = {
      ORIGINAL_VIDEOS_BUCKET_NAME = aws_s3_bucket.original_videos.bucket
    }
  }

  tags = {
    Name = "${var.project_name}-generateUploadUrl"
  }
}
