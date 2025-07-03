# logica_recursos/lambdas/createCourse/main.py
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
    Creates a new course.
    Expects a JSON body with 'title' and 'description'.
    """
    print(f"Request received: {event}")

    try:
        # En una aplicación real, verificaríamos si el usuario es un administrador.
        # user_groups = event['requestContext']['authorizer']['claims'].get('cognito:groups', [])
        # if 'admins' not in user_groups:
        #     return {
        #         'statusCode': 403,
        #         'body': json.dumps({'error': 'Forbidden: User is not an admin'})
        #     }

        body = json.loads(event.get('body', '{}'))
        title = body.get('title')
        description = body.get('description')

        if not title or not description:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Title and description are required'})
            }

        course_id = str(uuid.uuid4())
        
        item = {
            'PK': f"COURSE#{course_id}",
            'SK': "METADATA",
            'courseId': course_id,
            'title': title,
            'description': description,
            'createdAt': int(time.time())
        }

        print(f"Creating course item in DynamoDB: {item}")
        table.put_item(Item=item)
        print("Successfully created course.")

        return {
            'statusCode': 201,
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({'courseId': course_id, 'message': 'Course created successfully'})
        }

    except Exception as e:
        print(f"Error processing request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
