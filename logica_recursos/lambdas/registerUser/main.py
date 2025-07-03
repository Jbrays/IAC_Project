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
    log_data = {"function_name": context.function_name, "aws_request_id": context.aws_request_id}
    print(json.dumps({"level": "INFO", "message": "Request received", "details": log_data}))

    try:
        body = json.loads(event.get('body', '{}'))
        user_name = body.get('name')
        user_email = body.get('email')

        log_data["user_email"] = user_email

        if not user_name or not user_email:
            log_data["validation_error"] = "Name and email are required"
            print(json.dumps({"level": "WARN", "message": "Validation failed", "details": log_data}))
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Name and email are required'})
            }

        user_id = str(uuid.uuid4())
        item = {
            'PK': f"USER#{user_id}",
            'SK': f"PROFILE#{user_email}",
            'userId': user_id,
            'name': user_name,
            'email': user_email,
            'createdAt': context.aws_request_id
        }

        log_data["item_to_put"] = item
        print(json.dumps({"level": "INFO", "message": "Putting item into DynamoDB", "details": log_data}))
        table.put_item(Item=item)
        print(json.dumps({"level": "INFO", "message": "Successfully put item in DynamoDB", "details": log_data}))

        return {
            'statusCode': 201,
            'headers': {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            'body': json.dumps({'userId': user_id, 'message': 'User created successfully'})
        }

    except Exception as e:
        log_data["error"] = str(e)
        print(json.dumps({"level": "ERROR", "message": "Error processing request", "details": log_data}))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }