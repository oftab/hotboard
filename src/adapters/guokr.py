import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class GuokrAdapter(BaseAdapter):
    name = "guokr"
    platform = "果壳"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://www.guokr.com/apis/minisite/article.json"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        params = {"retrieve_type": "by_category", "limit": 30}
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers, params=params)
            if not response:
                return []
            try:
                data = response.json()
                return data.get("result", [])
            except:
                return []

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for i, item in enumerate(raw_data):
            try:
                title = item.get("title", "")
                url = item.get("url", "")
                hot_score = float(item.get("recommendations", 0) or 0)
                
                if title:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url or f"https://www.guokr.com/article/{item.get('id', '')}",
                        summary=item.get("summary", title)[:100],
                        hot_score=hot_score + 100 - i,
                        tags=["果壳", "科普"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing guokr item: {e}")
        return items
