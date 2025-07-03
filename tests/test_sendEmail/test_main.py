import pytest
import json
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logica_recursos', 'lambdas', 'sendEmail')))

os.environ['SENDER_EMAIL'] = 'sender@example.com'

from main import handler

@pytest.fixture
def mock_ses_client():
    with patch('main.ses_client') as mock_client:
        yield mock_client

@pytest.fixture
def sqs_event():
    """Genera un evento de SQS de ejemplo."""
    return {
        "Records": [
            {
                "messageId": "1",
                "body": json.dumps({
                    "recipient": "recipient@example.com",
                    "subject": "Test Subject",
                    "body_text": "Hello World",
                    "body_html": "<h1>Hello World</h1>"
                })
            }
        ]
    }

def test_send_email_success(mock_ses_client, sqs_event):
    """Prueba el envío de correo exitoso."""
    response = handler(sqs_event, {})

    assert response['statusCode'] == 200
    mock_ses_client.send_email.assert_called_once()
    
    # Verificar que los parámetros de send_email son correctos
    call_args, call_kwargs = mock_ses_client.send_email.call_args
    assert call_kwargs['Source'] == 'sender@example.com'
    assert call_kwargs['Destination']['ToAddresses'] == ['recipient@example.com']
    assert call_kwargs['Message']['Subject']['Data'] == 'Test Subject'

def test_send_email_malformed_message(mock_ses_client):
    """Prueba el manejo de un mensaje de SQS malformado."""
    event = {
        "Records": [
            {"messageId": "2", "body": json.dumps({"subject": "Missing fields"})}
        ]
    }
    response = handler(event, {})

    assert response['statusCode'] == 200 # La función no debe fallar
    mock_ses_client.send_email.assert_not_called() # No se debe intentar enviar el correo

def test_send_email_ses_error(mock_ses_client, sqs_event):
    """Prueba el manejo de errores de SES."""
    mock_ses_client.send_email.side_effect = Exception("SES Error")
    response = handler(sqs_event, {})

    assert response['statusCode'] == 200 # La función no debe fallar
    mock_ses_client.send_email.assert_called_once()
