import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class BilibiliAdapter(BaseAdapter):
    name = "bilibili"
    platform = "哔哩哔哩"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com/",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            data = response.json()
            return data.get("data", {}).get("list", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("title", "")
                bvid = item.get("bvid", "")
                url = f"https://www.bilibili.com/video/{bvid}" if bvid else ""
                desc = item.get("desc", "")
                stat = item.get("stat", {})
                hot_score = stat.get("view", 0) + stat.get("like", 0) * 2 + stat.get("coin", 0) * 10
                
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=desc[:100] if desc else title,
                        hot_score=float(hot_score),
                        tags=["B站", "视频"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing bilibili item: {e}")
        return items
