# lambda_startTranscoding.tf

# --- Lambda startTranscoding ---

# 1. Empaquetado del código fuente
data "archive_file" "start_transcoding_zip" {
  type        = "zip"
  source_dir  = "logica_recursos/lambdas/startTranscoding/"
  output_path = ".terraform/zips/startTranscoding.zip"
}

# 2. Rol de IAM para la Lambda
resource "aws_iam_role" "start_transcoding_lambda_role" {
  name = "${var.project_name}-startTranscoding-role"

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

# 3. Política de IAM para la Lambda (Logs y permiso para iniciar MediaConvert)
resource "aws_iam_policy" "start_transcoding_lambda_policy" {
  name        = "${var.project_name}-startTranscoding-policy"
  description = "IAM policy for startTranscoding Lambda"

  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Effect   = "Allow",
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action   = ["iam:PassRole"],
        Effect   = "Allow",
        Resource = aws_iam_role.mediaconvert_role.arn
      },
      {
        Action   = ["mediaconvert:CreateJob", "mediaconvert:DescribeEndpoints"],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

# 4. Adjuntar la política al rol de la Lambda
resource "aws_iam_role_policy_attachment" "start_transcoding_lambda_attach" {
  role       = aws_iam_role.start_transcoding_lambda_role.name
  policy_arn = aws_iam_policy.start_transcoding_lambda_policy.arn
}

# 5. Recurso de la Función Lambda
resource "aws_lambda_function" "start_transcoding" {
  function_name    = "${var.project_name}-startTranscoding"
  handler          = "main.handler"
  runtime          = "python3.9"
  role             = aws_iam_role.start_transcoding_lambda_role.arn
  filename         = data.archive_file.start_transcoding_zip.output_path
  source_code_hash = data.archive_file.start_transcoding_zip.output_base64sha256
  timeout          = 30

  environment {
    variables = {
      TRANSCODED_VIDEOS_BUCKET_NAME = aws_s3_bucket.transcoded_videos.bucket
      MEDIACONVERT_ROLE_ARN         = aws_iam_role.mediaconvert_role.arn
    }
  }
}

# --- Conexión S3 -> Lambda ---

# 6. Permiso para que S3 invoque la Lambda
resource "aws_lambda_permission" "s3_invoke_start_transcoding" {
  statement_id  = "AllowS3InvokeStartTranscoding"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.start_transcoding.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.original_videos.arn
}

# 7. Notificación en el bucket de S3
resource "aws_s3_bucket_notification" "video_upload_notification" {
  bucket = aws_s3_bucket.original_videos.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.start_transcoding.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "uploads/"
  }

  depends_on = [aws_lambda_permission.s3_invoke_start_transcoding]
}
