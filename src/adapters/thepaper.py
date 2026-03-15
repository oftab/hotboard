import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class ThepaperAdapter(BaseAdapter):
    name = "thepaper"
    platform = "澎湃新闻"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.thepaper.cn/",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            data = response.json()
            return data.get("data", {}).get("hotNews", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("name", "")
                cont_id = item.get("contId", "")
                url = f"https://www.thepaper.cn/newsDetail_forward_{cont_id}" if cont_id else ""
                hot_score = item.get("praiseTimes", 0)
                
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=f"澎湃新闻 - {title}",
                        hot_score=float(hot_score),
                        tags=["澎湃新闻", "新闻"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing thepaper item: {e}")
        return items
