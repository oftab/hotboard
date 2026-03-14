from .base import BaseAdapter
from ..models import HotItem


class HackerNewsAdapter(BaseAdapter):
    name = "hackernews"
    platform = "hacker-news"
    
    API_TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json"
    API_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"
    BASE_URL = "https://news.ycombinator.com"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher.get(self.API_TOP_STORIES)
            if not response:
                return []
            
            story_ids = response.json()[: self.config.max_items if self.config else 20]
            
            tasks = []
            for story_id in story_ids:
                url = self.API_ITEM.format(story_id)
                tasks.append(fetcher.get(url))
            
            import asyncio
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            items = []
            for resp in responses:
                if isinstance(resp, Exception):
                    continue
                if resp and resp.status_code == 200:
                    items.append(resp.json())
            
            return items

    def parse(self, raw_data: list[dict]) -> list[HotItem]:
        items = []
        
        for idx, story in enumerate(raw_data):
            if not story or not story.get("url"):
                continue
            
            title = story.get("title", "")
            url = story.get("url", "")
            score = story.get("score", 0) or 0
            descendants = story.get("descendants", 0) or 0
            
            hot_score = score + descendants * 0.5
            
            summary = f"{score} points | {descendants} comments"
            
            items.append(
                self._create_hot_item(
                    title=title,
                    url=url,
                    summary=summary,
                    hot_score=hot_score,
                    category="tech",
                    tags=["hacker-news", "tech"],
                )
            )
        
        return items
