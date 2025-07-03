# cognito.tf

# 1. Cognito User Pool
resource "aws_cognito_user_pool" "main" {
  name = "${var.project_name}-user-pool"

  # Requerir que el email sea verificado
  auto_verified_attributes = ["email"]

  # Definir los atributos del usuario
  schema {
    name                     = "email"
    attribute_data_type      = "String"
    mutable                  = false
    required                 = true
    string_attribute_constraints {
      min_length = 1
      max_length = 2048
    }
  }

  schema {
    name                     = "name"
    attribute_data_type      = "String"
    mutable                  = true
    required                 = true
    string_attribute_constraints {
      min_length = 1
      max_length = 256
    }
  }

  # Política de contraseñas
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  # Permitir que los administradores creen usuarios sin enviar una invitación inicial
  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  tags = {
    Name = "${var.project_name}-user-pool"
  }
}

# 2. Cognito User Pool Client
resource "aws_cognito_user_pool_client" "app_client" {
  name = "${var.project_name}-app-client"

  user_pool_id = aws_cognito_user_pool.main.id

  # Habilitar el flujo de autenticación con usuario y contraseña
  explicit_auth_flows = [
    "ALLOW_ADMIN_USER_PASSWORD_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]

  # No generar un secreto de cliente, ya que será usado por una app de navegador (pública)
  generate_secret = false
}


