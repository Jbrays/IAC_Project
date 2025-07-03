import pytest
import json
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logica_recursos', 'lambdas', 'enrollInCourse')))

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
        'body': json.dumps({'courseId': 'course-abc'})
    }

def test_enroll_success(mock_dynamodb_table, api_event):
    """Prueba la inscripción exitosa en un curso."""
    response = handler(api_event, {})

    assert response['statusCode'] == 201
    assert 'Successfully enrolled in course' in response['body']
    mock_dynamodb_table.put_item.assert_called_once()
    
    item = mock_dynamodb_table.put_item.call_args.kwargs['Item']
    assert item['PK'] == 'USER#user-123'
    assert item['SK'] == 'ENROLLMENT#course-abc'
    assert item['progress'] == 0

def test_enroll_no_course_id(mock_dynamodb_table, api_event):
    """Prueba la inscripción sin un courseId."""
    api_event['body'] = json.dumps({})
    response = handler(api_event, {})

    assert response['statusCode'] == 400
    assert 'courseId is required' in response['body']
    mock_dynamodb_table.put_item.assert_not_called()
