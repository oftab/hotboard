from .base import BaseAdapter
from ..models import HotItem


class WeiboAdapter(BaseAdapter):
    name = "weibo"
    platform = "weibo"
    
    API_URL = "https://weibo.com/ajax/side/hotSearch"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.API_URL)
            if not response or response.status_code != 200:
                return []
            
            data = response.json()
            realtime = data.get("data", {}).get("realtime", [])
            
            return realtime[: self.config.max_items if self.config else 30]

    def parse(self, raw_data: list[dict]) -> list[HotItem]:
        items = []
        
        for rank, topic in enumerate(raw_data, 1):
            if not topic:
                continue
            
            label = topic.get("label", "")
            word = topic.get("word", "")
            raw_url = topic.get("raw_url", "")
            num = topic.get("num", 0) or 0
            
            url = f"https://s.weibo.com/weibo?q={word}" if word else ""
            if raw_url and "weibo.com" not in raw_url:
                url = f"https://weibo.com{raw_url}" if raw_url.startswith("/") else raw_url
            
            hot_score = num
            
            summary = f"热度: {num:,}"
            
            items.append(
                self._create_hot_item(
                    title=word or label,
                    url=url,
                    summary=summary,
                    hot_score=hot_score,
                    category="social",
                    tags=["weibo", "trending", "weibo-hot"],
                )
            )
        
        return items
