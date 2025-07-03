# cloudwatch.tf

# 1. Regla de CloudWatch Events para capturar cambios de estado de MediaConvert
resource "aws_cloudwatch_event_rule" "mediaconvert_job_status_change" {
  name        = "${var.project_name}-mediaconvert-job-status-rule"
  description = "Capture MediaConvert job status changes"

  event_pattern = jsonencode({
    source      = ["aws.mediaconvert"],
    "detail-type" = ["MediaConvert Job State Change"],
    detail      = {
      status = ["COMPLETE", "ERROR"]
    }
  })
}

# 2. Objetivo de la regla: la Lambda updateVideoStatus
resource "aws_cloudwatch_event_target" "invoke_update_video_status_lambda" {
  rule      = aws_cloudwatch_event_rule.mediaconvert_job_status_change.name
  target_id = "InvokeUpdateVideoStatusLambda"
  arn       = aws_lambda_function.update_video_status.arn
}

# 3. Permiso para que CloudWatch Events invoque la Lambda
resource "aws_lambda_permission" "cloudwatch_invoke_update_video_status" {
  statement_id  = "AllowCloudWatchInvokeUpdateVideoStatus"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.update_video_status.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.mediaconvert_job_status_change.arn
}
