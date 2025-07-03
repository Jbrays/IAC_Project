# logica_recursos/lambdas/enrollInCourse/main.py
import json
import os
import boto3
import time

# Inicializar el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_NAME')
table = dynamodb.Table(table_name)

def handler(event, context):
    """
    Enrolls a user in a course.
    Expects a JSON body with 'courseId'.
    """
    print(f"Request received: {event}")

    try:
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        body = json.loads(event.get('body', '{}'))
        course_id = body.get('courseId')

        if not course_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'courseId is required'})
            }

        # Crear un ítem que representa la inscripción del usuario en el curso.
        # Usamos el mismo PK (USER#{userId}) pero un SK diferente para modelar la relación.
        item = {
            'PK': f"USER#{user_id}",
            'SK': f"ENROLLMENT#{course_id}",
            'courseId': course_id,
            'userId': user_id,
            'enrolledAt': int(time.time()),
            'progress': 0 # Iniciar el progreso en 0
        }

        print(f"Creating enrollment item in DynamoDB: {item}")
        table.put_item(Item=item)
        print("Successfully created enrollment.")

        return {
            'statusCode': 201,
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({'message': 'Successfully enrolled in course'})
        }

    except KeyError:
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
