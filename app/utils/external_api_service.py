import requests
import asyncio
import aiohttp
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExternalAPIService:
    """
    Service class to handle external API calls with proper error handling, 
    timeouts, and retry mechanisms
    """
    
    def __init__(self, base_url: str, timeout: int = 10, max_retries: int = 3):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
    
    def make_request(self, endpoint: str, method: str = "GET", 
                     headers: Optional[Dict] = None, 
                     params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make a synchronous request to the external API
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=self.timeout
                )
                
                if response.status_code in [200, 201]:
                    return response.json()
                elif response.status_code == 429:  # Rate limited
                    logger.warning(f"Rate limited on attempt {attempt + 1}, retrying...")
                    continue
                else:
                    logger.error(f"Request failed with status {response.status_code}: {response.text}")
                    if attempt == self.max_retries - 1:
                        return None
                        
            except requests.exceptions.Timeout:
                logger.error(f"Request timed out on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    return None
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    return None
        
        return None

    async def make_async_request(self, endpoint: str, method: str = "GET", 
                                headers: Optional[Dict] = None, 
                                params: Optional[Dict] = None, 
                                data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make an asynchronous request to the external API
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        json=data,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 429:  # Rate limited
                            logger.warning(f"Rate limited on attempt {attempt + 1}, retrying...")
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        else:
                            logger.error(f"Request failed with status {response.status}: {await response.text()}")
                            if attempt == self.max_retries - 1:
                                return None
                                
            except asyncio.TimeoutError:
                logger.error(f"Request timed out on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    return None
            except aiohttp.ClientError as e:
                logger.error(f"Client error on attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    return None
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    return None
        
        return None