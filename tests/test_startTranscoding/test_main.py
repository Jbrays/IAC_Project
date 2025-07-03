import pytest
import json
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logica_recursos', 'lambdas', 'startTranscoding')))

# Establecer variables de entorno simuladas
os.environ['TRANSCODED_VIDEOS_BUCKET_NAME'] = 'test-transcoded-bucket'
os.environ['MEDIACONVERT_ROLE_ARN'] = 'arn:aws:iam::123456789012:role/MediaConvertRole'

from main import handler

@pytest.fixture
def mock_boto3_client():
    """Fixture para simular el cliente de boto3."""
    with patch('main.boto3.client') as mock_client_constructor:
        mock_mc_client = MagicMock()
        # Simular la respuesta de describe_endpoints
        mock_mc_client.describe_endpoints.return_value = {'Endpoints': [{'Url': 'https://mediaconvert.test.com'}]}
        
        # El constructor devuelve diferentes mocks según el servicio
        def client_side_effect(service_name, endpoint_url=None):
            if service_name == 'mediaconvert':
                return mock_mc_client
            return MagicMock()
            
        mock_client_constructor.side_effect = client_side_effect
        yield mock_mc_client

@pytest.fixture
def s3_event():
    """Genera un evento de S3 de ejemplo."""
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "test-original-bucket"},
                    "object": {"key": "uploads/video.mp4"}
                }
            }
        ]
    }

def test_start_transcoding_success(mock_boto3_client, s3_event):
    """Prueba el inicio exitoso de un trabajo de transcodificación."""
    response = handler(s3_event, {})

    assert response['statusCode'] == 200
    assert 'Transcoding job started successfully' in response['body']
    mock_boto3_client.create_job.assert_called_once()
    
    # Verificar que los datos correctos se pasaron a create_job
    call_args, call_kwargs = mock_boto3_client.create_job.call_args
    assert call_kwargs['Role'] == 'arn:aws:iam::123456789012:role/MediaConvertRole'
    assert call_kwargs['Settings']['Inputs'][0]['FileInput'] == 's3://test-original-bucket/uploads/video.mp4'
    assert 'userMetadata' in call_kwargs
    assert call_kwargs['userMetadata']['sourceObjectKey'] == 'uploads/video.mp4'

def test_start_transcoding_mediaconvert_error(mock_boto3_client, s3_event):
    """Prueba el manejo de errores al crear el trabajo en MediaConvert."""
    mock_boto3_client.create_job.side_effect = Exception("MediaConvert Error")

    with pytest.raises(Exception, match="MediaConvert Error"):
        handler(s3_event, {})
