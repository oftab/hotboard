import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class XiaohongshuAdapter(BaseAdapter):
    name = "xiaohongshu"
    platform = "小红书"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://edith.xiaohongshu.com/api/sns/web/v1/hot_search/list"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.xiaohongshu.com/",
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
                title = item.get("search_word", "")
                hot_value = item.get("hot_value", 0)
                url = f"https://www.xiaohongshu.com/search_result?keyword={title}"
                
                if title:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=f"小红书热搜 - {title}",
                        hot_score=float(hot_value),
                        tags=["小红书", "生活"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing xiaohongshu item: {e}")
        return items
