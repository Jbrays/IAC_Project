import pytest
import json
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logica_recursos', 'lambdas', 'generateUploadUrl')))

from main import handler

@pytest.fixture
def mock_s3_client():
    with patch('main.s3_client') as mock_client:
        yield mock_client

@pytest.fixture
def api_gateway_event():
    return {
        'body': json.dumps({
            'fileName': 'video.mp4',
            'fileType': 'video/mp4'
        })
    }

def test_generate_url_success(mock_s3_client, api_gateway_event):
    """Prueba la generación exitosa de una URL prefirmada."""
    test_url = "https://s3.test.com/upload-here"
    mock_s3_client.generate_presigned_url.return_value = test_url
    
    response = handler(api_gateway_event, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['uploadUrl'] == test_url
    assert 'key' in body
    mock_s3_client.generate_presigned_url.assert_called_once()

def test_generate_url_missing_fields(mock_s3_client):
    """Prueba la llamada con campos faltantes."""
    event = {'body': json.dumps({'fileName': 'video.mp4'})} # Falta fileType
    response = handler(event, {})

    assert response['statusCode'] == 400
    assert 'fileName and fileType are required' in response['body']
    mock_s3_client.generate_presigned_url.assert_not_called()

def test_generate_url_s3_error(mock_s3_client, api_gateway_event):
    """Prueba el manejo de errores del cliente S3."""
    from botocore.exceptions import ClientError
    mock_s3_client.generate_presigned_url.side_effect = ClientError({'Error': {'Code': '500', 'Message': 'S3 Error'}}, 'generate_presigned_url')
    
    response = handler(api_gateway_event, {})

    assert response['statusCode'] == 500
    assert 'Could not generate upload URL' in response['body']
