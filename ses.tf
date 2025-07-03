# ses.tf

# 1. Recurso para gestionar y verificar la identidad del correo electrónico remitente.
# Al ejecutar `terraform apply`, AWS enviará un correo de verificación a esta dirección.
# El proceso de apply se pausará hasta que se haga clic en el enlace de dicho correo.
resource "aws_ses_email_identity" "main" {
  email = var.sender_email
}
