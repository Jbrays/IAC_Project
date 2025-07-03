# Plataforma de E-learning Serverless en AWS

Este proyecto implementa una arquitectura de backend completa para una plataforma de e-learning utilizando tecnologías serverless de AWS, desplegada y gestionada a través de Terraform.

## Prerrequisitos

Antes de empezar, asegúrate de tener lo siguiente:

1.  **Cuenta de AWS:** Una cuenta de AWS con permisos para crear los recursos necesarios.
2.  **AWS CLI:** Instalada y configurada. [Instrucciones](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).
3.  **Terraform:** Instalado en tu máquina local (versión ~1.5.0). [Instrucciones](https://learn.hashicorp.com/tutorials/terraform/install-cli).
4.  **Git y una cuenta de GitHub:** Para clonar el repositorio y utilizar el pipeline de GitHub Actions.
5.  **Python:** Versión 3.9 o superior.

## Guía de Configuración y Despliegue

Sigue estos pasos para desplegar la infraestructura en tu propia cuenta de AWS.

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Jbrays/IAC_Project.git
cd IAC_Project
```

### 2. Configuración de Variables

Abre el archivo `variables.tf` y modifica los valores por defecto si es necesario. El más importante es:

-   **`sender_email`**: Asegúrate de que el valor por defecto de esta variable sea una dirección de correo electrónico a la que tengas acceso y que puedas verificar.

### 3. Verificación de Identidad en SES

Para que el sistema pueda enviar correos, debes verificar tu identidad de remitente en Amazon SES.

1.  Navega a la consola de **Amazon Simple Email Service (SES)** en tu cuenta de AWS.
2.  Ve a **Verified identities** y haz clic en **Create identity**.
3.  Selecciona "Email address", introduce la misma dirección que configuraste en `variables.tf` y sigue los pasos.
4.  Recibirás un correo de verificación. Haz clic en el enlace para completar el proceso.
5.  **Importante:** Por defecto, tu cuenta de SES estará en modo "sandbox", lo que significa que solo podrás enviar correos *a* direcciones también verificadas.

### 4. Despliegue con GitHub Actions (Método Recomendado)

1.  **Sube el código a tu repositorio de GitHub.**

2.  **Configura los Secrets de GitHub:**
    *   En tu repositorio de GitHub, ve a `Settings` > `Secrets and variables` > `Actions`.
    *   Crea los siguientes "Repository secrets" con tus credenciales de AWS:
        *   `AWS_ACCESS_KEY_ID`
        *   `AWS_SECRET_ACCESS_KEY`
        *   `AWS_SESSION_TOKEN` (necesario si usas credenciales temporales de SSO).

3.  **Activa el Pipeline:**
    *   Haz un `push` a la rama `main` de tu repositorio.
        ```bash
        git push origin main
        ```
    *   Ve a la pestaña **"Actions"** en tu repositorio de GitHub para ver el pipeline ejecutarse. El pipeline se encargará de probar, analizar y desplegar la infraestructura.

### 5. Despliegue Manual (Alternativa)

Si prefieres desplegar desde tu terminal:

1.  **Autentícate en AWS:**
    ```bash
    aws sso login --profile TU_PERFIL # Si usas SSO
    ```

2.  **Inicializa Terraform:**
    ```bash
    terraform init
    ```

3.  **Aplica la configuración:**
    ```bash
    terraform apply -auto-approve
    ```
