import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class DevToAdapter(BaseAdapter):
    name = "devto"
    platform = "Dev.to"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://dev.to/api/articles?per_page=30&top=1"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            return response.json()

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("title", "")
                url = item.get("url", "")
                description = item.get("description", "")
                positive_reactions = item.get("positive_reactions_count", 0)
                comments = item.get("comments_count", 0)
                cover = item.get("cover_image", "")
                tags_list = item.get("tag_list", [])
                
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=description or title,
                        hot_score=float(positive_reactions * 2 + comments * 5),
                        image_url=cover,
                        tags=["Dev.to"] + tags_list[:2],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing devto item: {e}")
        return items
