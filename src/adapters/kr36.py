import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class Kr36Adapter(BaseAdapter):
    name = "kr36"
    platform = "36氪"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://gateway.36kr.com/api/mis/nav/home/nav/rank/hot"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://36kr.com/",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            data = response.json()
            return data.get("data", {}).get("itemList", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("title", "")
                item_id = item.get("itemId", "")
                url = f"https://36kr.com/p/{item_id}" if item_id else ""
                summary = item.get("summary", "")
                stat = item.get("stat", {})
                hot_score = stat.get("pv", 0) + stat.get("like", 0) * 10
                
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=summary[:100] if summary else title,
                        hot_score=float(hot_score),
                        tags=["36氪", "科技"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing kr36 item: {e}")
        return items
