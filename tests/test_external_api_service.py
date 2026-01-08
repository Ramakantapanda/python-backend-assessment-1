import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from app.utils.external_api_service import ExternalAPIService


@pytest.fixture
def api_service():
    return ExternalAPIService(base_url="https://jsonplaceholder.typicode.com", timeout=5, max_retries=2)


def test_external_api_service_init():
    """Test initialization of ExternalAPIService"""
    service = ExternalAPIService(base_url="https://api.example.com", timeout=10, max_retries=3)
    assert service.base_url == "https://api.example.com"
    assert service.timeout == 10
    assert service.max_retries == 3


@patch('requests.request')
def test_make_request_success(mock_request):
    """Test successful request to external API"""
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.return_value = {"id": 1, "title": "Test", "body": "Test body", "userId": 1}
    
    service = ExternalAPIService(base_url="https://api.example.com")
    result = service.make_request("posts/1")
    
    assert result == {"id": 1, "title": "Test", "body": "Test body", "userId": 1}
    mock_request.assert_called_once()


@patch('requests.request')
def test_make_request_with_timeout(mock_request):
    """Test request with timeout error"""
    from requests.exceptions import Timeout
    mock_request.side_effect = Timeout()
    
    service = ExternalAPIService(base_url="https://api.example.com", max_retries=1)
    result = service.make_request("posts/1")
    
    assert result is None


@patch('requests.request')
def test_make_request_with_connection_error(mock_request):
    """Test request with connection error"""
    from requests.exceptions import ConnectionError
    mock_request.side_effect = ConnectionError()
    
    service = ExternalAPIService(base_url="https://api.example.com", max_retries=1)
    result = service.make_request("posts/1")
    
    assert result is None


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.request', new_callable=AsyncMock)
async def test_make_async_request_success(mock_request):
    """Test successful async request to external API"""
    # Mock the response object
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"id": 1, "title": "Test", "body": "Test body", "userId": 1})
    mock_request.return_value.__aenter__.return_value = mock_response
    
    service = ExternalAPIService(base_url="https://api.example.com")
    result = await service.make_async_request("posts/1")
    
    assert result == {"id": 1, "title": "Test", "body": "Test body", "userId": 1}


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.request', new_callable=AsyncMock)
async def test_make_async_request_timeout(mock_request):
    """Test async request with timeout"""
    from asyncio import TimeoutError
    mock_request.side_effect = TimeoutError()
    
    service = ExternalAPIService(base_url="https://api.example.com", max_retries=1)
    result = await service.make_async_request("posts/1")
    
    assert result is None