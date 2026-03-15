import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class ProductHuntAdapter(BaseAdapter):
    name = "producthunt"
    platform = "Product Hunt"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://www.producthunt.com/frontend/graphql"
        self.query = """
        query {
            posts(order: RANKING, first: 30) {
                edges {
                    node {
                        id
                        name
                        tagline
                        url
                        votesCount
                        commentsCount
                        thumbnail {
                            url
                        }
                    }
                }
            }
        }
        """

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
        }
        payload = {"query": self.query}
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher._client.post(self.api_url, json=payload, headers=headers)
            if response.status_code != 200:
                return []
            data = response.json()
            edges = data.get("data", {}).get("posts", {}).get("edges", [])
            return [edge.get("node", {}) for edge in edges]

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                name = item.get("name", "")
                tagline = item.get("tagline", "")
                url = item.get("url", "")
                votes = item.get("votesCount", 0)
                thumbnail = item.get("thumbnail", {}).get("url", "")
                
                if name:
                    full_url = f"https://www.producthunt.com{url}" if url.startswith("/") else url
                    items.append(self._create_hot_item(
                        title=name,
                        url=full_url,
                        summary=tagline,
                        hot_score=float(votes),
                        image_url=thumbnail,
                        tags=["ProductHunt", "产品"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing producthunt item: {e}")
        return items
