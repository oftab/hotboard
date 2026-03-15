from dataclasses import dataclass, field
from typing import Optional
from yaml import safe_load


@dataclass
class AdapterConfig:
    name: str
    enabled: bool = True
    priority: int = 100
    timeout: int = 30
    max_items: int = 20
    url: Optional[str] = None
    rss_urls: list[str] = field(default_factory=list)
    headers: dict = field(default_factory=dict)
    category: str = "general"
    icon: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "AdapterConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "priority": self.priority,
            "timeout": self.timeout,
            "max_items": self.max_items,
            "url": self.url,
            "rss_urls": self.rss_urls,
            "headers": self.headers,
            "category": self.category,
            "icon": self.icon,
        }


def load_config(config_path: str = "config.yaml") -> dict[str, AdapterConfig]:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = safe_load(f)
    except FileNotFoundError:
        return get_default_config()
    
    if not data or "adapters" not in data:
        return get_default_config()
    
    configs = {}
    for name, config_data in data.get("adapters", {}).items():
        if isinstance(config_data, dict):
            config_data["name"] = name
            configs[name] = AdapterConfig.from_dict(config_data)
        elif isinstance(config_data, bool):
            configs[name] = AdapterConfig(name=name, enabled=config_data)
    
    return configs


def get_default_config() -> dict[str, AdapterConfig]:
    return {
        "hackernews": AdapterConfig(
            name="hackernews",
            enabled=True,
            priority=10,
            url="https://hacker-news.firebaseio.com/v0",
            category="tech",
            icon="https://news.ycombinator.com/favicon.ico",
        ),
        "github_trending": AdapterConfig(
            name="github_trending",
            enabled=True,
            priority=20,
            url="https://api.github.com",
            category="tech",
            icon="https://github.com/favicon.ico",
        ),
        "reddit": AdapterConfig(
            name="reddit",
            enabled=True,
            priority=30,
            url="https://www.reddit.com",
            category="social",
            icon="https://www.reddit.com/favicon.ico",
        ),
        "weibo": AdapterConfig(
            name="weibo",
            enabled=True,
            priority=40,
            url="https://weibo.com/ajax/side/hotSearch",
            category="social",
            icon="https://weibo.com/favicon.ico",
        ),
        "rss": AdapterConfig(
            name="rss",
            enabled=True,
            priority=50,
            rss_urls=[
                "https://feeds.bbci.co.uk/news/world/rss.xml",
                "https://www.reutersagency.com/feed/?best-topics=tech",
            ],
            category="news",
            icon="https://www.bbc.com/favicon.ico",
        ),
    }
