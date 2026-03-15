import json
from typing import Optional
from .base import BaseAdapter
from ..models import AdapterConfig


class KuaishouAdapter(BaseAdapter):
    name = "kuaishou"
    platform = "快手"

    def __init__(self, config: Optional[AdapterConfig] = None):
        super().__init__(config)
        self.api_url = "https://www.kuaishou.com/graphql"

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Referer": "https://www.kuaishou.com/",
        }
        payload = {
            "operationName": "hotSearchQuery",
            "query": "query hotSearchQuery { hotSearchList { searchWord hotValue } }",
            "variables": {}
        }
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            response = await fetcher._client.post(self.api_url, json=payload, headers=headers)
            if response.status_code != 200:
                return []
            data = response.json()
            return data.get("data", {}).get("hotSearchList", [])

    def parse(self, raw_data: list[dict]) -> list:
        items = []
        for item in raw_data:
            try:
                title = item.get("searchWord", "")
                hot_value = item.get("hotValue", 0)
                url = f"https://www.kuaishou.com/search/video?searchKey={title}"
                
                if title:
                    items.append(self._create_hot_item(
                        title=title,
                        url=url,
                        summary=f"快手热搜 - {title}",
                        hot_score=float(hot_value),
                        tags=["快手", "短视频"],
                    ))
            except Exception as e:
                self.logger.warning(f"Error parsing kuaishou item: {e}")
        return items
