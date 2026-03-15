from .base import BaseAdapter
from ..models import HotItem


class RedditAdapter(BaseAdapter):
    name = "reddit"
    platform = "reddit"
    
    SUBREDDITS = ["technology", "programming", "worldnews", "science", " gadgets"]

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            posts = []
            
            headers = {
                "User-Agent": "HotBoard/1.0",
            }
            
            for subreddit in self.SUBREDDITS:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json"
                params = {"limit": self.config.max_items if self.config else 10}
                
                try:
                    response = await fetcher.get(url, headers=headers, params=params)
                    if response and response.status_code == 200:
                        data = response.json()
                        children = data.get("data", {}).get("children", [])
                        for child in children:
                            post = child.get("data", {})
                            post["subreddit"] = subreddit
                            posts.append(post)
                except Exception as e:
                    self.logger.warning(f"Error fetching r/{subreddit}: {e}")
            
            return posts[: self.config.max_items if self.config else 30]

    def parse(self, raw_data: list[dict]) -> list[HotItem]:
        items = []
        
        for post in raw_data:
            if not post:
                continue
            
            title = post.get("title", "")
            url = post.get("url", "")
            permalink = post.get("permalink", "")
            score = post.get("score", 0) or 0
            num_comments = post.get("num_comments", 0) or 0
            subreddit = post.get("subreddit", "")
            
            if not url:
                url = f"https://reddit.com{permalink}"
            
            hot_score = score + num_comments * 2
            
            summary = f"⬆️ {score} | 💬 {num_comments} | r/{subreddit}"
            
            items.append(
                self._create_hot_item(
                    title=title,
                    url=url,
                    summary=summary,
                    hot_score=hot_score,
                    category="social",
                    tags=["reddit", f"r/{subreddit}"],
                )
            )
        
        return items
