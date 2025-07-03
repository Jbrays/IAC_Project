# logica_recursos/lambdas/registerUser/main.py
import json
import os
import boto3
import uuid

# Inicializar el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_NAME')
table = dynamodb.Table(table_name)

def handler(event, context):
    """
    Handles user registration.
    Expects a JSON body with 'name' and 'email'.
    """
    print(f"Request received: {event}")

    try:
        # Parsear el cuerpo de la solicitud
        body = json.loads(event.get('body', '{}'))
        user_name = body.get('name')
        user_email = body.get('email')

        if not user_name or not user_email:
            print("Validation Failed: name and email are required.")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Name and email are required'})
            }

        # Crear el item para DynamoDB
        user_id = str(uuid.uuid4())
        item = {
            'PK': f"USER#{user_id}",
            'SK': f"PROFILE#{user_email}",
            'userId': user_id,
            'name': user_name,
            'email': user_email,
            'createdAt': context.aws_request_id # Usamos el request ID como timestamp simple
        }

        # Guardar en DynamoDB
        print(f"Putting item into DynamoDB: {item}")
        table.put_item(Item=item)
        print("Successfully put item in DynamoDB")

        return {
            'statusCode': 201,
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({'userId': user_id, 'message': 'User created successfully'})
        }

    except Exception as e:
        print(f"Error processing request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
