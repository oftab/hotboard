import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class TmtPostAdapter(BaseAdapter):
    name = "tmtpost"
    platform = "钛媒体"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://www.tmtpost.com/hot/"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.tmtpost.com/",
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers)
            if not response:
                return []
            return [{"html": response.text}]

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        if not raw_data:
            return items
        
        html = raw_data[0].get("html", "")
        import re
        
        pattern = r'<a[^>]*href="([^"]*tmtpost[^"]*)"[^>]*>([^<]{5,})</a>'
        matches = re.findall(pattern, html)
        
        for i, (url, title) in enumerate(matches[:30]):
            try:
                title = title.strip()
                if title and url:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=f"钛媒体热点 - {title}",
                        hot_score=float(100 - i),
                        tags=["钛媒体", "科技"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing tmtpost item: {e}")
        return items
