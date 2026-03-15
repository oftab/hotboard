import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class JuejinAdapter(BaseAdapter):
    name = "juejin"
    platform = "掘金"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://api.juejin.cn/recommend_api/v1/article/recommend_cate_feed"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
        }
        payload = {
            "id_type": 2,
            "sort_type": 200,
            "cate_id": "6809637773935378440",
            "cursor": "0",
            "limit": 30
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher._client.post(self.api_url, json=payload, headers=headers)
            if response.status_code != 200:
                return []
            data = response.json()
            return data.get("data", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                article_info = item.get("article_info", {})
                title = article_info.get("title", "")
                article_id = article_info.get("article_id", "")
                brief_content = article_info.get("brief_content", "")
                view_count = article_info.get("view_count", 0)
                digg_count = article_info.get("digg_count", 0)
                
                if title and article_id:
                    url = f"https://juejin.cn/post/{article_id}"
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=brief_content[:100] if brief_content else title,
                        hot_score=float(view_count + digg_count * 10),
                        tags=["掘金", "技术"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing juejin item: {e}")
        return items
