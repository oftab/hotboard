import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class ZhihuDailyAdapter(BaseAdapter):
    name = "zhihu_daily"
    platform = "知乎日报"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://news-at.zhihu.com/api/4/news/latest"

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
            return data.get("stories", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("title", "")
                story_id = item.get("id", "")
                url = f"https://daily.zhihu.com/story/{story_id}" if story_id else ""
                summary = item.get("hint", "")
                
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=summary or title,
                        hot_score=float(100 - raw_data.index(item)),
                        tags=["知乎日报", "阅读"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing zhihu_daily item: {e}")
        return items
