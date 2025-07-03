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

### 3. Despliegue Inicial y Verificación de Email

Este proyecto utiliza Terraform para gestionar la verificación de la identidad de correo en SES. Esto introduce un paso manual durante el primer despliegue.

1.  **Autentícate en AWS:** Asegúrate de que tu AWS CLI esté configurada.
    ```bash
    aws sso login --profile TU_PERFIL # Si usas SSO
    ```

2.  **Inicializa Terraform:**
    ```bash
    terraform init
    ```

3.  **Aplica la configuración:**
    ```bash
    terraform apply
    ```
    - Terraform comenzará a crear los recursos y se **pausará** al llegar al recurso `aws_ses_email_identity`.
    - En este momento, **revisa la bandeja de entrada** del correo especificado en la variable `sender_email`.
    - **Haz clic en el enlace de verificación** que te ha enviado Amazon Web Services.
    - Una vez verificado, Terraform detectará el cambio y completará el despliegue.

### 4. Despliegue Automatizado con GitHub Actions

Una vez que la identidad de SES ha sido verificada en el primer `apply`, los despliegues futuros a través del pipeline serán totalmente automáticos.

1.  **Sube el código a tu repositorio de GitHub.**

2.  **Configura los Secrets de GitHub:**
    *   En tu repositorio de GitHub, ve a `Settings` > `Secrets and variables` > `Actions`.
    *   Crea los siguientes "Repository secrets":
        *   `AWS_ACCESS_KEY_ID`
        *   `AWS_SECRET_ACCESS_KEY`
        *   `AWS_SESSION_TOKEN` (necesario si usas credenciales temporales).

3.  **Activa el Pipeline:**
    *   Haz un `push` a la rama `main`.
    *   Ve a la pestaña **"Actions"** en tu repositorio para ver el pipeline ejecutarse.

