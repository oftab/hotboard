import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class DingxiangAdapter(BaseAdapter):
    name = "dingxiang"
    platform = "丁香医生"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://dxy.com/app/i/ask/hotlist"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://dxy.com/",
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
                question_id = item.get("questionId", "")
                url = f"https://dxy.com/question/{question_id}" if question_id else ""
                hot_score = item.get("likeCount", 0)
                
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=f"丁香医生热门问答 - {title}",
                        hot_score=float(hot_score),
                        tags=["丁香医生", "健康"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing dingxiang item: {e}")
        return items
