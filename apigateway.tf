# apigateway.tf

# 1. API Gateway (HTTP API)
resource "aws_apigatewayv2_api" "main" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = ["*"] # Abierto para pruebas. En producción, debería ser la URL del frontend.
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization", "X-Amz-Date", "X-Api-Key", "X-Amz-Security-Token"]
  }
}

# 2. Integración para la función getCourses
resource "aws_apigatewayv2_integration" "get_courses" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.get_courses.invoke_arn
}

# --- Autorizador de Cognito ---
resource "aws_apigatewayv2_authorizer" "cognito_auth" {
  api_id           = aws_apigatewayv2_api.main.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "cognito-authorizer"

  jwt_configuration {
    audience = [aws_cognito_user_pool_client.app_client.id]
    issuer   = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.main.id}"
  }
}

# 3. Ruta para la función getCourses (GET /courses) - PROTEGIDA
resource "aws_apigatewayv2_route" "get_courses" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /courses"
  target    = "integrations/${aws_apigatewayv2_integration.get_courses.id}"

  # Proteger esta ruta con el autorizador de Cognito
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_auth.id
}

# 4. Permiso para que API Gateway invoque la Lambda getCourses
resource "aws_lambda_permission" "api_gateway_get_courses" {
  statement_id  = "AllowAPIGatewayInvokeGetCourses"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_courses.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# 5. Etapa de despliegue (e.g., /v1)
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true
}

# --- Integración para registerUser ---

# 6. Integración para la función registerUser
resource "aws_apigatewayv2_integration" "register_user" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.register_user.invoke_arn
}

# 7. Ruta para la función registerUser (POST /users)
resource "aws_apigatewayv2_route" "register_user" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /users"
  target    = "integrations/${aws_apigatewayv2_integration.register_user.id}"
}

# --- Integración para generateUploadUrl ---

# 9. Integración para la función generateUploadUrl
resource "aws_apigatewayv2_integration" "generate_upload_url" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.generate_upload_url.invoke_arn
}

# 10. Ruta para la función generateUploadUrl (POST /courses/upload-url)
resource "aws_apigatewayv2_route" "generate_upload_url" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /courses/upload-url"
  target    = "integrations/${aws_apigatewayv2_integration.generate_upload_url.id}"

  # Proteger esta ruta
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_auth.id
}

# --- Integración para purchaseCourse ---

# 12. Integración para la función purchaseCourse
resource "aws_apigatewayv2_integration" "purchase_course" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.purchase_course.invoke_arn
}

# 13. Ruta para la función purchaseCourse (POST /purchase)
resource "aws_apigatewayv2_route" "purchase_course" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /purchase"
  target    = "integrations/${aws_apigatewayv2_integration.purchase_course.id}"

  # Proteger esta ruta
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_auth.id
}

# --- Integración para createCourse ---

# 15. Integración para la función createCourse
resource "aws_apigatewayv2_integration" "create_course" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.create_course.invoke_arn
}

# 16. Ruta para la función createCourse (POST /courses)
resource "aws_apigatewayv2_route" "create_course" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /courses"
  target    = "integrations/${aws_apigatewayv2_integration.create_course.id}"

  # Proteger esta ruta
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_auth.id
}

# --- Integración para enrollInCourse ---

# 18. Integración para la función enrollInCourse
resource "aws_apigatewayv2_integration" "enroll_in_course" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.enroll_in_course.invoke_arn
}

# 19. Ruta para la función enrollInCourse (POST /enroll)
resource "aws_apigatewayv2_route" "enroll_in_course" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /enroll"
  target    = "integrations/${aws_apigatewayv2_integration.enroll_in_course.id}"

  # Proteger esta ruta
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_auth.id
}

# --- Integración para trackProgress ---

# 21. Integración para la función trackProgress
resource "aws_apigatewayv2_integration" "track_progress" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.track_progress.invoke_arn
}

# 22. Ruta para la función trackProgress (POST /progress)
resource "aws_apigatewayv2_route" "track_progress" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /progress"
  target    = "integrations/${aws_apigatewayv2_integration.track_progress.id}"

  # Proteger esta ruta
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_auth.id
}

# --- Integración para generateCertificate ---

# 24. Integración para la función generateCertificate
resource "aws_apigatewayv2_integration" "generate_certificate" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.generate_certificate.invoke_arn
}

# 25. Ruta para la función generateCertificate (POST /certificate)
resource "aws_apigatewayv2_route" "generate_certificate" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /certificate"
  target    = "integrations/${aws_apigatewayv2_integration.generate_certificate.id}"

  # Proteger esta ruta
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_auth.id
}

# 26. Permiso para que API Gateway invoque la Lambda generateCertificate
resource "aws_lambda_permission" "api_gateway_generate_certificate" {
  statement_id  = "AllowAPIGatewayInvokeGenerateCertificate"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.generate_certificate.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# 23. Permiso para que API Gateway invoque la Lambda trackProgress
resource "aws_lambda_permission" "api_gateway_track_progress" {
  statement_id  = "AllowAPIGatewayInvokeTrackProgress"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.track_progress.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# 20. Permiso para que API Gateway invoque la Lambda enrollInCourse
resource "aws_lambda_permission" "api_gateway_enroll_in_course" {
  statement_id  = "AllowAPIGatewayInvokeEnrollInCourse"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.enroll_in_course.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# 17. Permiso para que API Gateway invoque la Lambda createCourse
resource "aws_lambda_permission" "api_gateway_create_course" {
  statement_id  = "AllowAPIGatewayInvokeCreateCourse"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_course.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# 14. Permiso para que API Gateway invoque la Lambda purchaseCourse
resource "aws_lambda_permission" "api_gateway_purchase_course" {
  statement_id  = "AllowAPIGatewayInvokePurchaseCourse"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.purchase_course.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# 11. Permiso para que API Gateway invoque la Lambda generateUploadUrl
resource "aws_lambda_permission" "api_gateway_generate_upload_url" {
  statement_id  = "AllowAPIGatewayInvokeGenerateUploadUrl"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.generate_upload_url.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# 8. Permiso para que API Gateway invoque la Lambda registerUser
resource "aws_lambda_permission" "api_gateway_register_user" {
  statement_id  = "AllowAPIGatewayInvokeRegisterUser"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.register_user.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}
