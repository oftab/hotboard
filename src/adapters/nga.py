import json
import re
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class NgaAdapter(BaseAdapter):
    name = "nga"
    platform = "NGA论坛"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://ngabbs.com/api/threads"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get("https://ngabbs.com/", headers=headers)
            if not response:
                return []
            return [{"html": response.text}]

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        if not raw_data:
            return items
        
        html = raw_data[0].get("html", "")
        pattern = r'<a[^>]*href="([^"]*)"[^>]*title="([^"]*)"[^>]*>'
        matches = re.findall(pattern, html)
        
        for i, (url, title) in enumerate(matches[:30]):
            try:
                title = title.strip()
                if title and len(title) > 2:
                    items.append(self._create_hot_item(
                        title=title,
                        url=f"https://ngabbs.com{url}" if url.startswith("/") else url,
                        summary=f"NGA热帖 - {title}",
                        hot_score=float(100 - i),
                        tags=["NGA", "游戏"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing nga item: {e}")
        return items
