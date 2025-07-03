import json
import pytest
from unittest.mock import patch, MagicMock
import os
import sys

# Añadir el directorio de la Lambda al path para poder importarla
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logica_recursos', 'lambdas', 'getCourses')))

from main import handler

@pytest.fixture
def mock_dynamodb():
    """Fixture para simular DynamoDB."""
    with patch('main.boto3.resource') as mock_resource:
        mock_dynamodb_instance = MagicMock()
        mock_table = MagicMock()
        mock_resource.return_value = mock_dynamodb_instance
        mock_dynamodb_instance.Table.return_value = mock_table
        yield mock_table

def test_get_courses_success(mock_dynamodb):
    """Prueba el caso de éxito para obtener cursos."""
    # Configurar el mock para devolver una lista de cursos
    mock_courses = [
        {'id': 'c001', 'title': 'Curso 1'},
        {'id': 'c002', 'title': 'Curso 2'}
    ]
    mock_dynamodb.scan.return_value = {'Items': mock_courses}

    # Llamar al handler
    response = handler({}, {})

    # Verificar la respuesta
    assert response['statusCode'] == 200
    assert response['body'] == json.dumps(mock_courses)
    mock_dynamodb.scan.assert_called_once()

def test_get_courses_dynamodb_error(mock_dynamodb):
    """Prueba el manejo de errores de DynamoDB."""
    # Configurar el mock para que lance una excepción
    mock_dynamodb.scan.side_effect = Exception("DynamoDB Error")

    # Llamar al handler
    response = handler({}, {})

    # Verificar la respuesta de error
    assert response['statusCode'] == 500
    assert 'Internal Server Error' in response['body']
