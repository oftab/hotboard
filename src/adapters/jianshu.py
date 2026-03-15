import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class JianshuAdapter(BaseAdapter):
    name = "jianshu"
    platform = "简书"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://www.jianshu.com/asimov/trending/notes"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        params = {"count": 30, "note_ids": ""}
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers, params=params)
            if not response:
                return []
            try:
                data = response.json()
                return data.get("notes", [])
            except:
                return []

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for i, item in enumerate(raw_data):
            try:
                title = item.get("title", "")
                slug = item.get("slug", "")
                hot_score = float(item.get("likes_count", 0) or 0)
                
                if title:
                    items.append(self._create_hot_item(
                        title=title,
                        url=f"https://www.jianshu.com/p/{slug}" if slug else "",
                        summary=item.get("abstract", title)[:100],
                        hot_score=hot_score + 100 - i,
                        tags=["简书", "写作"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing jianshu item: {e}")
        return items
