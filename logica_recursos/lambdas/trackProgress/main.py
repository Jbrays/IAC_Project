# logica_recursos/lambdas/trackProgress/main.py
import json
import os
import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_NAME')
table = dynamodb.Table(table_name)

def handler(event, context):
    """
    Updates a user's progress in a course.
    Expects a JSON body with 'courseId' and 'progress' (a number between 0 and 100).
    """
    print(f"Request received: {event}")

    try:
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        body = json.loads(event.get('body', '{}'))
        course_id = body.get('courseId')
        progress = body.get('progress')

        if not course_id or progress is None:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'courseId and progress are required'})
            }

        if not isinstance(progress, (int, float)) or not (0 <= progress <= 100):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Progress must be a number between 0 and 100'})
            }

        # The key for the enrollment item
        key = {
            'PK': f"USER#{user_id}",
            'SK': f"ENROLLMENT#{course_id}"
        }

        # Update the progress attribute
        update_expression = "SET progress = :p"
        expression_attribute_values = {":p": progress}

        print(f"Updating progress for user {user_id} in course {course_id} to {progress}")
        
        response = table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )
        
        print(f"Successfully updated progress. New attributes: {response.get('Attributes')}")

        return {
            'statusCode': 200,
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({'message': 'Progress updated successfully'})
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
