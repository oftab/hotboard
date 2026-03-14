from datetime import datetime, timezone
from typing import Optional
from ..models import HotItem, HotBoard


class Aggregator:
    def __init__(self, max_items: int = 100):
        self.max_items = max_items

    def deduplicate(self, items: list[HotItem]) -> list[HotItem]:
        seen_urls = set()
        unique_items = []
        
        for item in items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        return unique_items

    def merge_boards(self, boards: list[HotBoard]) -> HotBoard:
        merged = HotBoard()
        
        for board in boards:
            for item in board.items:
                merged.add_item(item)
        
        merged.items = self.deduplicate(merged.items)
        
        self._calculate_scores(merged.items)
        
        merged.sort_by_score()
        
        merged.items = merged.items[:self.max_items]
        
        return merged

    def _calculate_scores(self, items: list[HotItem]) -> None:
        if not items:
            return
        
        max_score = max(item.hot_score for item in items)
        
        source_weights = {
            "hackernews": 1.2,
            "github_trending": 1.2,
            "reddit": 1.1,
            "twitter": 1.0,
            "weibo": 1.0,
            "rss": 0.9,
            "default": 1.0,
        }
        
        for item in items:
            weight = source_weights.get(item.source, source_weights["default"])
            
            base_score = item.hot_score if item.hot_score > 0 else 1
            
            normalized_score = (base_score / max_score) * 100 if max_score > 0 else 50
            
            item.hot_score = normalized_score * weight

    def filter_by_category(self, items: list[HotItem], category: str) -> list[HotItem]:
        return [item for item in items if item.category == category]

    def filter_by_source(self, items: list[HotItem], source: str) -> list[HotItem]:
        return [item for item in items if item.source == source]

    def get_top_by_source(self, items: list[HotItem], source: str, top_n: int = 10) -> list[HotItem]:
        source_items = self.filter_by_source(items, source)
        source_items.sort(key=lambda x: x.hot_score, reverse=True)
        return source_items[:top_n]
