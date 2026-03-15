import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class HupuAdapter(BaseAdapter):
    name = "hupu"
    platform = "虎扑"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://m.hupu.com/api/bbs/topics"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get("https://m.hupu.com/api/bbs/topics?fid=34", headers=headers)
            if not response:
                return []
            try:
                data = response.json()
                return data.get("data", {}).get("list", [])
            except:
                return []

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for i, item in enumerate(raw_data):
            try:
                title = item.get("title", "")
                url = item.get("url", "")
                hot_score = float(item.get("replies", 0) or 0)
                
                if title:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url or f"https://m.hupu.com/bbs/{item.get('tid', '')}",
                        summary=f"虎扑热帖 - {title}",
                        hot_score=hot_score + 100 - i,
                        tags=["虎扑", "体育"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing hupu item: {e}")
        return items
