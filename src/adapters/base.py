from abc import ABC, abstractmethod
from typing import Optional
import logging
from datetime import datetime, timezone
from ..models import HotItem, AdapterConfig
from ..core import Fetcher


logger = logging.getLogger(__name__)


class BaseAdapter(ABC):
    name: str = "base"
    platform: str = "unknown"
    config: Optional[AdapterConfig] = None
    
    def __init__(self, config: Optional[AdapterConfig] = None):
        self.config = config or AdapterConfig(name=self.name)
        self.logger = logging.getLogger(f"adapter.{self.name}")

    @abstractmethod
    async def fetch(self) -> list[dict]:
        """从平台获取原始数据"""
        pass

    @abstractmethod
    def parse(self, raw_data: list[dict]) -> list[HotItem]:
        """解析原始数据为HotItem列表"""
        pass

    async def run(self) -> list[HotItem]:
        """执行完整的抓取和解析流程"""
        if not self.config or not self.config.enabled:
            self.logger.info(f"Adapter {self.name} is disabled, skipping")
            return []
        
        try:
            self.logger.info(f"Starting fetch for {self.name}")
            raw_data = await self.fetch()
            self.logger.info(f"Fetched {len(raw_data)} raw items from {self.name}")
            
            items = self.parse(raw_data)
            self.logger.info(f"Parsed {len(items)} items from {self.name}")
            
            return items
        except Exception as e:
            self.logger.error(f"Error running adapter {self.name}: {e}")
            return []

    def _create_hot_item(
        self,
        title: str,
        url: str,
        summary: str = "",
        hot_score: float = 0,
        category: Optional[str] = None,
        published_at: Optional[str] = None,
        image_url: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> HotItem:
        return HotItem(
            title=title,
            summary=summary or title,
            url=url,
            source=self.name,
            hot_score=hot_score,
            category=category or self.config.category if self.config else "general",
            published_at=published_at or datetime.now(timezone.utc).isoformat(),
            image_url=image_url,
            source_icon=self.config.icon if self.config else None,
            tags=tags or [],
        )
