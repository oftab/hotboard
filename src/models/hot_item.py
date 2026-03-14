from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional
import uuid
import hashlib


@dataclass
class HotItem:
    title: str
    summary: str
    url: str
    source: str
    hot_score: float
    category: str
    published_at: str
    image_url: Optional[str] = None
    source_icon: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    fetched_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        content = f"{self.source}:{self.url}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class HotBoard:
    version: str = "1.0"
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    items: list[HotItem] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)

    def add_item(self, item: HotItem) -> None:
        self.items.append(item)
        if item.source not in self.sources:
            self.sources.append(item.source)
    
    def add_items(self, items: list[HotItem]) -> None:
        for item in items:
            self.add_item(item)
    
    def sort_by_score(self, descending: bool = True) -> None:
        self.items.sort(key=lambda x: x.hot_score, reverse=descending)
    
    def sort_by_time(self, descending: bool = True) -> None:
        self.items.sort(key=lambda x: x.published_at, reverse=descending)
    
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "generatedAt": self.generated_at,
            "items": [item.to_dict() for item in self.items],
            "sources": self.sources,
        }
    
    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "HotBoard":
        board = cls(
            version=data.get("version", "1.0"),
            generated_at=data.get("generatedAt", datetime.now(timezone.utc).isoformat()),
        )
        for item_data in data.get("items", []):
            board.add_item(HotItem(**item_data))
        return board
