# logica_recursos/lambdas/updateVideoStatus/main.py
import json
import os
import boto3
from urllib.parse import unquote_plus

# Inicializar el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_NAME')
table = dynamodb.Table(table_name)

def handler(event, context):
    """
    Updates the video status in DynamoDB based on MediaConvert job events.
    """
    print(f"Request received: {event}")

    try:
        # Extraer detalles del evento de MediaConvert
        job_status = event['detail']['status']
        job_id = event['detail']['jobId']
        
        # La información del input está en la configuración del trabajo
        # Necesitamos obtenerla para saber qué video se procesó.
        input_details = event['detail']['userMetadata']
        original_s3_uri = input_details['sourceS3'] # Asumiendo que pasamos esto como metadata

        # El object key es parte de la URI de S3
        # Ejemplo: s3://bucket-name/uploads/video.mp4 -> uploads/video.mp4
        object_key = '/'.join(original_s3_uri.split('/')[3:])
        # Decodificar en caso de caracteres especiales en el nombre del archivo
        object_key = unquote_plus(object_key)

        print(f"Job {job_id} finished with status: {job_status} for video: {object_key}")

        # Aquí, necesitaríamos una forma de mapear el 'object_key' a un item en DynamoDB.
        # Por ahora, simplemente registraremos el evento. En una implementación completa,
        # se buscaría el item en DynamoDB (quizás por el 'object_key') y se actualizaría.
        
        # En una implementación real, se buscaría el item del curso/video
        # y se actualizaría. Por ahora, solo registramos el evento.
        # Ejemplo de cómo podría ser (requiere un diseño de tabla que lo soporte):
        # table.update_item(
        #     Key={'PK': f"COURSE#{course_id}", 'SK': f"VIDEO#{object_key}"},
        #     UpdateExpression="set videoStatus = :s, transcodedAt = :t",
        #     ExpressionAttributeValues={':s': job_status, ':t': int(time.time())}
        # )

        print(f"Video status update processed for {object_key} with status {job_status} (simulated).")

        return {
            'statusCode': 200,
            'body': json.dumps(f"Processed status {job_status} for job {job_id}")
        }

    except Exception as e:
        print(f"Error processing MediaConvert event: {e}")
        raise e
