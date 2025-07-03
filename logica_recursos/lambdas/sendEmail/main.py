# logica_recursos/lambdas/sendEmail/main.py
import json
import os
import boto3

# Inicializar el cliente de SES
ses_client = boto3.client('ses')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')

def handler(event, context):
    """
    Processes messages from an SQS queue and sends emails using SES.
    """
    print(f"Request received: {event}")

    for record in event['Records']:
        try:
            message_body = json.loads(record['body'])
            
            recipient_email = message_body.get('recipient')
            subject = message_body.get('subject')
            body_text = message_body.get('body_text')
            body_html = message_body.get('body_html')

            if not all([recipient_email, subject, body_text, body_html]):
                print(f"Skipping malformed message: {record['messageId']}")
                continue

            print(f"Sending email to {recipient_email} with subject '{subject}'")

            ses_client.send_email(
                Source=SENDER_EMAIL,
                Destination={
                    'ToAddresses': [
                        recipient_email,
                    ],
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body_text,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': body_html,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            
            print(f"Successfully sent email for message: {record['messageId']}")

        except Exception as e:
            print(f"Error processing message {record.get('messageId', 'N/A')}: {e}")
            # No relanzar la excepción para evitar que el mensaje vuelva a la cola
            # y cause un bucle de envenenamiento. En un sistema real, se enviaría a una Dead Letter Queue.
            pass
    
    return {
        'statusCode': 200,
        'body': json.dumps('Finished processing messages.')
    }
