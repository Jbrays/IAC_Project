import pytest
import json
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logica_recursos', 'lambdas', 'createCourse')))

os.environ['DYNAMODB_TABLE_NAME'] = 'test-table'

from main import handler

@pytest.fixture
def mock_dynamodb_table():
    with patch('main.table') as mock_table:
        yield mock_table

@pytest.fixture
def api_event():
    return {
        'body': json.dumps({
            'title': 'New Course',
            'description': 'A great course.'
        })
    }

def test_create_course_success(mock_dynamodb_table, api_event):
    """Prueba la creación de un curso exitosa."""
    response = handler(api_event, {})

    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert 'courseId' in body
    mock_dynamodb_table.put_item.assert_called_once()
    
    item = mock_dynamodb_table.put_item.call_args.kwargs['Item']
    assert item['title'] == 'New Course'
    assert item['SK'] == 'METADATA'

def test_create_course_missing_fields(mock_dynamodb_table):
    """Prueba la creación de un curso con campos faltantes."""
    event = {'body': json.dumps({'title': 'Incomplete Course'})}
    response = handler(event, {})

    assert response['statusCode'] == 400
    assert 'Title and description are required' in response['body']
    mock_dynamodb_table.put_item.assert_not_called()
