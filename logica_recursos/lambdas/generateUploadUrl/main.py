# logica_recursos/lambdas/generateUploadUrl/main.py
import json
import os
import boto3
import uuid
from botocore.exceptions import ClientError

# Inicializar el cliente de S3
s3_client = boto3.client('s3')
bucket_name = os.environ.get('ORIGINAL_VIDEOS_BUCKET_NAME')

def handler(event, context):
    """
    Generates a pre-signed URL for uploading a video to S3.
    Expects a JSON body with 'fileName' and 'fileType'.
    """
    print(f"Request received: {event}")

    try:
        # Parsear el cuerpo de la solicitud
        body = json.loads(event.get('body', '{}'))
        file_name = body.get('fileName')
        file_type = body.get('fileType')

        if not file_name or not file_type:
            print("Validation Failed: fileName and fileType are required.")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'fileName and fileType are required'})
            }

        # Generar un nombre de archivo único para evitar colisiones
        object_key = f"uploads/{uuid.uuid4()}-{file_name}"

        # Generar la URL prefirmada
        print(f"Generating pre-signed URL for {object_key} in bucket {bucket_name}")
        
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key,
                'ContentType': file_type
            },
            ExpiresIn=3600  # La URL es válida por 1 hora
        )

        print("Successfully generated pre-signed URL.")

        return {
            'statusCode': 200,
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({
                'uploadUrl': presigned_url,
                'key': object_key
            })
        }

    except ClientError as e:
        print(f"Error generating pre-signed URL: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Could not generate upload URL'})
        }
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
