# logica_recursos/lambdas/purchaseCourse/main.py
import json
import os
import boto3
import uuid
import time

# Inicializar el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_NAME')
table = dynamodb.Table(table_name)

def handler(event, context):
    """
    Handles a course purchase.
    Expects a JSON body with 'courseId'.
    The user ID is extracted from the Cognito authorizer context.
    """
    print(f"Request received: {event}")

    try:
        # Extraer el ID de usuario del contexto del autorizador de Cognito
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Parsear el cuerpo de la solicitud
        body = json.loads(event.get('body', '{}'))
        course_id = body.get('courseId')

        if not course_id:
            print("Validation Failed: courseId is required.")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'courseId is required'})
            }

        # Simular llamada a la API de Stripe (en un caso real, esto sería una petición HTTP)
        print("Simulating call to Stripe API...")
        time.sleep(1) # Simular latencia de red
        print("Stripe payment successful (simulated).")

        # Crear el item de compra para DynamoDB
        purchase_id = str(uuid.uuid4())
        item = {
            'PK': f"USER#{user_id}",
            'SK': f"COURSE#{course_id}",
            'purchaseId': purchase_id,
            'purchasedAt': int(time.time())
        }

        # Guardar en DynamoDB
        print(f"Putting item into DynamoDB: {item}")
        table.put_item(Item=item)
        print("Successfully recorded purchase in DynamoDB")

        return {
            'statusCode': 201,
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({'purchaseId': purchase_id, 'message': 'Course purchased successfully'})
        }

    except KeyError:
        print("Error: Could not extract user ID from token.")
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Forbidden - User not authenticated'})
        }
    except Exception as e:
        print(f"Error processing request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
