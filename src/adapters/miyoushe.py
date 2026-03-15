import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class MiyousheAdapter(BaseAdapter):
    name = "miyoushe"
    platform = "米游社"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://bbs-api.miyoushe.com/post/wapi/getForumPostList"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        params = {"forum_id": 43, "is_good": "true", "is_hot": "true", "page_size": 30}
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.api_url, headers=headers, params=params)
            if not response:
                return []
            try:
                data = response.json()
                return data.get("data", {}).get("list", [])
            except:
                return []

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for i, item in enumerate(raw_data):
            try:
                post = item.get("post", {})
                title = post.get("subject", "")
                url = f"https://www.miyoushe.com/ys/article/{post.get('post_id', '')}"
                hot_score = float(post.get("stat", {}).get("view_num", 0) or 0)
                
                if title:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=post.get("content", title)[:100],
                        hot_score=hot_score + 100 - i,
                        tags=["米游社", "游戏"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing miyoushe item: {e}")
        return items
