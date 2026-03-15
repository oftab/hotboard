import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class TiebaAdapter(BaseAdapter):
    name = "tieba"
    platform = "百度贴吧"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://tieba.baidu.com/hottopic/browse/topicList"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://tieba.baidu.com/",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            data = response.json()
            return data.get("data", {}).get("topic_list", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("topic_name", "")
                url = item.get("topic_url", "")
                discuss_num = item.get("discuss_num", 0)
                
                if title:
                    full_url = f"https://tieba.baidu.com{url}" if url.startswith("/") else url
                    items.append(self._create_hot_item(
                        title=title,
                        url=full_url,
                        summary=f"贴吧热议 - {title}",
                        hot_score=float(discuss_num),
                        tags=["贴吧", "社区"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing tieba item: {e}")
        return items
