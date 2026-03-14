import httpx
import asyncio


class Fetcher:
    def __init__(self, timeout: int = 10, max_retries: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def get(self, url: str, **kwargs):
        if not self._client:
            return None
        
        for attempt in range(self.max_retries):
            try:
                response = await self._client.get(url, **kwargs)
                if response.status_code == 200:
                    return response
            except Exception:
                await asyncio.sleep(1)
        return None
