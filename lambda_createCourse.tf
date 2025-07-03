# lambda_createCourse.tf

# 1. Empaquetado del código fuente
data "archive_file" "create_course_zip" {
  type        = "zip"
  source_dir  = "logica_recursos/lambdas/createCourse/"
  output_path = ".terraform/zips/createCourse.zip"
}

# 2. Rol de IAM
resource "aws_iam_role" "create_course_lambda_role" {
  name = "${var.project_name}-createCourse-role"

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

# 3. Política de IAM (Logs y escritura en DynamoDB)
resource "aws_iam_policy" "create_course_lambda_policy" {
  name        = "${var.project_name}-createCourse-policy"
  description = "IAM policy for createCourse Lambda"

  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Effect   = "Allow",
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action   = ["dynamodb:PutItem"],
        Effect   = "Allow",
        Resource = aws_dynamodb_table.main_table.arn
      }
    ]
  })
}

# 4. Adjuntar la política al rol
resource "aws_iam_role_policy_attachment" "create_course_lambda_attach" {
  role       = aws_iam_role.create_course_lambda_role.name
  policy_arn = aws_iam_policy.create_course_lambda_policy.arn
}

# 5. Recurso de la Función Lambda
resource "aws_lambda_function" "create_course" {
  function_name    = "${var.project_name}-createCourse"
  handler          = "main.handler"
  runtime          = "python3.9"
  role             = aws_iam_role.create_course_lambda_role.arn
  filename         = data.archive_file.create_course_zip.output_path
  source_code_hash = data.archive_file.create_course_zip.output_base64sha256

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.main_table.name
    }
  }

  tags = {
    Name = "${var.project_name}-createCourse"
  }
}
