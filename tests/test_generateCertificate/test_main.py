import pytest
import json
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logica_recursos', 'lambdas', 'generateCertificate')))

os.environ['DYNAMODB_TABLE_NAME'] = 'test-table'
os.environ['SQS_QUEUE_URL'] = 'http://test.queue.url'
os.environ['COGNITO_USER_POOL_ID'] = 'test-pool-id'

from main import handler

@pytest.fixture
def mock_boto3_clients():
    with patch('main.dynamodb') as mock_dynamodb, \
         patch('main.sqs_client') as mock_sqs, \
         patch('main.cognito_client') as mock_cognito:
        
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        
        yield mock_table, mock_sqs, mock_cognito

@pytest.fixture
def api_event():
    return {
        'requestContext': {'authorizer': {'claims': {'sub': 'user-123', 'username': 'testuser'}}},
        'body': json.dumps({'courseId': 'course-abc'})
    }

def test_cert_generate_success(mock_boto3_clients, api_event):
    """Prueba la generación de certificado exitosa."""
    mock_table, mock_sqs, mock_cognito = mock_boto3_clients
    
    # Simular que el usuario completó el curso y existe en Cognito
    mock_table.get_item.side_effect = [
        {'Item': {'progress': 100}}, # Primer get_item para el progreso
        {'Item': {'title': 'Amazing Course'}} # Segundo get_item para el título
    ]
    mock_cognito.admin_get_user.return_value = {
        'UserAttributes': [{'Name': 'email', 'Value': 'test@example.com'}]
    }

    response = handler(api_event, {})

    assert response['statusCode'] == 200
    assert 'Certificate generation initiated' in response['body']
    mock_sqs.send_message.assert_called_once()
    
    # Verificar el mensaje enviado a SQS
    message_body = json.loads(mock_sqs.send_message.call_args.kwargs['MessageBody'])
    assert message_body['recipient'] == 'test@example.com'
    assert 'Amazing Course' in message_body['subject']

def test_cert_generate_course_not_completed(mock_boto3_clients, api_event):
    """Prueba el caso en que el curso no está completado."""
    mock_table, mock_sqs, _ = mock_boto3_clients
    mock_table.get_item.return_value = {'Item': {'progress': 50}}

    response = handler(api_event, {})

    assert response['statusCode'] == 400
    assert 'Course not completed yet' in response['body']
    mock_sqs.send_message.assert_not_called()
