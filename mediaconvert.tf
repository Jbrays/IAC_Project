# mediaconvert.tf

# 1. Rol de IAM para que MediaConvert acceda a S3
resource "aws_iam_role" "mediaconvert_role" {
  name = "${var.project_name}-mediaconvert-role"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "mediaconvert.amazonaws.com"
      }
    }]
  })
}

# 2. Política para el rol de MediaConvert
resource "aws_iam_policy" "mediaconvert_policy" {
  name        = "${var.project_name}-mediaconvert-policy"
  description = "IAM policy for MediaConvert to access S3"

  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action   = ["s3:GetObject", "s3:PutObject"],
        Effect   = "Allow",
        Resource = [
          "${aws_s3_bucket.original_videos.arn}/*",
          "${aws_s3_bucket.transcoded_videos.arn}/*"
        ]
      }
    ]
  })
}

# 3. Adjuntar la política al rol
resource "aws_iam_role_policy_attachment" "mediaconvert_attach" {
  role       = aws_iam_role.mediaconvert_role.name
  policy_arn = aws_iam_policy.mediaconvert_policy.arn
}
