import pytest
import json
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logica_recursos', 'lambdas', 'registerUser')))

from main import handler

@pytest.fixture
def mock_dynamodb_table():
    with patch('main.table') as mock_table:
        yield mock_table

@pytest.fixture
def api_gateway_event():
    """Genera un evento de API Gateway de ejemplo."""
    return {
        'body': json.dumps({
            'name': 'Test User',
            'email': 'test@example.com'
        })
    }

def test_register_user_success(mock_dynamodb_table, api_gateway_event):
    """Prueba el registro de usuario exitoso."""
    context = {'aws_request_id': 'test_request_id'}
    response = handler(api_gateway_event, context)

    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert 'userId' in body
    assert body['message'] == 'User created successfully'
    mock_dynamodb_table.put_item.assert_called_once()

def test_register_user_missing_fields(mock_dynamodb_table):
    """Prueba el registro de usuario con campos faltantes."""
    event = {'body': json.dumps({'name': 'Test User'})} # Falta el email
    response = handler(event, {})

    assert response['statusCode'] == 400
    assert 'Name and email are required' in response['body']
    mock_dynamodb_table.put_item.assert_not_called()

def test_register_user_dynamodb_error(mock_dynamodb_table, api_gateway_event):
    """Prueba el manejo de errores de DynamoDB."""
    mock_dynamodb_table.put_item.side_effect = Exception("DynamoDB Error")
    context = {'aws_request_id': 'test_request_id'}
    response = handler(api_gateway_event, context)

    assert response['statusCode'] == 500
    assert 'Internal Server Error' in response['body']
