import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class DouyinAdapter(BaseAdapter):
    name = "douyin"
    platform = "抖音"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/"

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
            return data.get("word_list", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("word", "")
                hot_value = item.get("hot_value", 0)
                url = f"https://www.douyin.com/search/{title}"
                
                if title:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=f"抖音热搜 - {title}",
                        hot_score=float(hot_value),
                        tags=["抖音", "短视频"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing douyin item: {e}")
        return items
