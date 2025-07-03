import pytest
import json
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logica_recursos', 'lambdas', 'purchaseCourse')))

os.environ['DYNAMODB_TABLE_NAME'] = 'test-table'

from main import handler

@pytest.fixture
def mock_dynamodb_table():
    with patch('main.table') as mock_table:
        yield mock_table

@pytest.fixture
def api_event():
    """Genera un evento de API Gateway con contexto de autorizador."""
    return {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'user-123'
                }
            }
        },
        'body': json.dumps({
            'courseId': 'course-abc'
        })
    }

def test_purchase_course_success(mock_dynamodb_table, api_event):
    """Prueba la compra de un curso exitosa."""
    response = handler(api_event, {})

    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert 'purchaseId' in body
    assert body['message'] == 'Course purchased successfully'
    mock_dynamodb_table.put_item.assert_called_once()
    
    # Verificar que el item guardado es correcto
    call_args, call_kwargs = mock_dynamodb_table.put_item.call_args
    item = call_kwargs['Item']
    assert item['PK'] == 'USER#user-123'
    assert item['SK'] == 'COURSE#course-abc'

def test_purchase_course_no_course_id(mock_dynamodb_table, api_event):
    """Prueba el caso en que falta el courseId."""
    api_event['body'] = json.dumps({}) # Sin courseId
    response = handler(api_event, {})

    assert response['statusCode'] == 400
    assert 'courseId is required' in response['body']
    mock_dynamodb_table.put_item.assert_not_called()

def test_purchase_course_no_auth(mock_dynamodb_table):
    """Prueba el caso sin información de autenticación."""
    event = {'body': json.dumps({'courseId': 'course-abc'})} # Sin requestContext
    response = handler(event, {})

    assert response['statusCode'] == 500 # Debería ser un error interno por el KeyError
    assert 'Internal Server Error' in response['body']
