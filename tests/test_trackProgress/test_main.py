import pytest
import json
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logica_recursos', 'lambdas', 'trackProgress')))

os.environ['DYNAMODB_TABLE_NAME'] = 'test-table'

from main import handler

@pytest.fixture
def mock_dynamodb_table():
    with patch('main.table') as mock_table:
        yield mock_table

@pytest.fixture
def api_event():
    return {
        'requestContext': {'authorizer': {'claims': {'sub': 'user-123'}}},
        'body': json.dumps({'courseId': 'course-abc', 'progress': 50})
    }

def test_track_progress_success(mock_dynamodb_table, api_event):
    """Prueba la actualización de progreso exitosa."""
    mock_dynamodb_table.update_item.return_value = {'Attributes': {'progress': 50}}
    response = handler(api_event, {})

    assert response['statusCode'] == 200
    assert 'Progress updated successfully' in response['body']
    mock_dynamodb_table.update_item.assert_called_once()
    
    call_kwargs = mock_dynamodb_table.update_item.call_args.kwargs
    assert call_kwargs['Key'] == {'PK': 'USER#user-123', 'SK': 'ENROLLMENT#course-abc'}
    assert call_kwargs['UpdateExpression'] == "SET progress = :p"
    assert call_kwargs['ExpressionAttributeValues'] == {":p": 50}

def test_track_progress_invalid_value(mock_dynamodb_table, api_event):
    """Prueba la actualización con un valor de progreso inválido."""
    api_event['body'] = json.dumps({'courseId': 'course-abc', 'progress': 101})
    response = handler(api_event, {})

    assert response['statusCode'] == 400
    assert 'Progress must be a number between 0 and 100' in response['body']
    mock_dynamodb_table.update_item.assert_not_called()
