import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class InfoQAdapter(BaseAdapter):
    name = "infoq"
    platform = "InfoQ"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://www.infoq.cn/public/v1/article/gethotlist"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Referer": "https://www.infoq.cn/",
        }
        payload = {"size": 30}
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher._client.post(self.api_url, json=payload, headers=headers)
            if response.status_code != 200:
                return []
            data = response.json()
            return data.get("data", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("article_title", "")
                uuid = item.get("uuid", "")
                url = f"https://www.infoq.cn/article/{uuid}" if uuid else ""
                summary = item.get("article_summary", "")
                hot_score = item.get("view_count", 0) + item.get("like_count", 0) * 10
                
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=summary[:100] if summary else title,
                        hot_score=float(hot_score),
                        tags=["InfoQ", "技术"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing infoq item: {e}")
        return items
