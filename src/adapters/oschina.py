import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class OschinaAdapter(BaseAdapter):
    name = "oschina"
    platform = "开源中国"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://www.oschina.net/news/ajax_news_list?show=hot"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.oschina.net/",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            data = response.json()
            return data.get("data", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("title", "")
                url = item.get("href", "")
                summary = item.get("summary", "")
                hot_score = item.get("viewCount", 0) + item.get("commentCount", 0) * 5
                
                if title and url:
                    full_url = f"https://www.oschina.net{url}" if url.startswith("/") else url
                    items.append(self._create_hot_item(
                        title=title,
                        url=full_url,
                        summary=summary[:100] if summary else title,
                        hot_score=float(hot_score),
                        tags=["开源中国", "开源"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing oschina item: {e}")
        return items
