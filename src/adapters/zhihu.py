import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class ZhihuAdapter(BaseAdapter):
    name = "zhihu"
    platform = "知乎"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
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
                target = item.get("target", {})
                title = target.get("title", "")
                url = target.get("url", "")
                excerpt = target.get("excerpt", "")
                hot_value = item.get("detail_text", "0")
                hot_score = float(hot_value.replace("万", "0000").replace("亿", "00000000")) if hot_value else 0
                
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=excerpt or title,
                        hot_score=hot_score,
                        tags=["知乎", "问答"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing zhihu item: {e}")
        return items
