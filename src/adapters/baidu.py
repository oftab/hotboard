import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class BaiduAdapter(BaseAdapter):
    name = "baidu"
    platform = "百度热搜"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://top.baidu.com/api/board?platform=wise&tab=realtime"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            data = response.json()
            return data.get("data", {}).get("cards", [{}])[0].get("content", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("word", "")
                url = item.get("url", "")
                hot_score = item.get("hotScore", 0)
                desc = item.get("desc", "")
                
                if title:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url or f"https://www.baidu.com/s?wd={title}",
                        summary=desc or f"百度热搜 - {title}",
                        hot_score=float(hot_score),
                        tags=["百度", "搜索"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing baidu item: {e}")
        return items
