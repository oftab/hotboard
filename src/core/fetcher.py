import httpx
from typing import Optional
import asyncio


class Fetcher:
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def get(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Optional[httpx.Response]:
        if not self._client:
            raise RuntimeError("Fetcher must be used as async context manager")

        merged_headers = {**self._client.headers, **(headers or {})}

        for attempt in range(self.max_retries):
            try:
                response = await self._client.get(url, headers=merged_headers, params=params)
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    wait_time = 2**attempt
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return response
            except httpx.RequestError as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)

        return None

    async def post(
        self,
        url: str,
        data: Optional[dict] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> Optional[httpx.Response]:
        if not self._client:
            raise RuntimeError("Fetcher must be used as async context manager")

        merged_headers = {**self._client.headers, **(headers or {})}

        for attempt in range(self.max_retries):
            try:
                response = await self._client.post(
                    url, data=data, json=json, headers=merged_headers
                )
                return response
            except httpx.RequestError as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)

        return None
