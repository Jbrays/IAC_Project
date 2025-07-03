import pytest
import json
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logica_recursos', 'lambdas', 'updateVideoStatus')))

os.environ['DYNAMODB_TABLE_NAME'] = 'test-table'

from main import handler

@pytest.fixture
def mock_dynamodb_table():
    with patch('main.table') as mock_table:
        yield mock_table

@pytest.fixture
def mediaconvert_event():
    """Genera un evento de MediaConvert de ejemplo."""
    return {
        "detail": {
            "status": "COMPLETE",
            "jobId": "12345",
            "userMetadata": {
                "sourceObjectKey": "uploads/video.mp4"
            }
        }
    }

def test_update_status_success(mock_dynamodb_table, mediaconvert_event):
    """Prueba la actualización de estado exitosa (simulada)."""
    response = handler(mediaconvert_event, {})

    assert response['statusCode'] == 200
    assert 'Processed status COMPLETE for job 12345' in response['body']
    
    # Como la actualización está comentada, verificamos que no se llama
    mock_dynamodb_table.update_item.assert_not_called()

def test_update_status_error_event(mock_dynamodb_table):
    """Prueba el manejo de un evento malformado."""
    event = {"detail": {"status": "ERROR"}} # Falta userMetadata
    
    with pytest.raises(Exception):
        handler(event, {})
    
    mock_dynamodb_table.update_item.assert_not_called()
