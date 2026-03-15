from .base import BaseAdapter
from ..models import HotItem
import feedparser
from datetime import datetime, timezone
from dateutil import parser as date_parser


class RSSAdapter(BaseAdapter):
    name = "rss"
    platform = "rss"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        if not self.config or not self.config.rss_urls:
            return []
        
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            all_entries = []
            
            for feed_url in self.config.rss_urls:
                try:
                    response = await fetcher.get(feed_url)
                    if not response or response.status_code != 200:
                        continue
                    
                    feed = feedparser.parse(response.text)
                    
                    for entry in feed.entries[: self.config.max_items if self.config else 10]:
                        entry_data = {
                            "title": entry.get("title", ""),
                            "summary": entry.get("summary", ""),
                            "link": entry.get("link", ""),
                            "published": entry.get("published", ""),
                            "feed_title": feed.feed.get("title", ""),
                            "feed_url": feed_url,
                            "tags": [tag.term for tag in entry.get("tags", [])],
                        }
                        all_entries.append(entry_data)
                        
                except Exception as e:
                    self.logger.warning(f"Error fetching RSS feed {feed_url}: {e}")
            
            return all_entries

    def parse(self, raw_data: list[dict]) -> list[HotItem]:
        items = []
        
        for entry in raw_data:
            if not entry:
                continue
            
            title = entry.get("title", "")
            url = entry.get("link", "")
            summary = entry.get("summary", "")
            published = entry.get("published", "")
            feed_title = entry.get("feed_title", "RSS")
            tags = entry.get("tags", [])
            
            if not url:
                continue
            
            hot_score = 50
            
            parsed_date = None
            try:
                if published:
                    parsed_date = date_parser.parse(published)
                    parsed_date = parsed_date.astimezone(timezone.utc)
            except Exception:
                pass
            
            from ..core.parser import Parser
            clean_summary = Parser.extract_text(summary, 200)
            
            items.append(
                self._create_hot_item(
                    title=title,
                    url=url,
                    summary=clean_summary or f"来源: {feed_title}",
                    hot_score=hot_score,
                    category="news",
                    published_at=parsed_date.isoformat() if parsed_date else None,
                    tags=tags or ["rss", feed_title.lower().replace(" ", "-")],
                )
            )
        
        return items
