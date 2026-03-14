import asyncio
import argparse
import logging
import sys
from pathlib import Path

from src.config import Settings
from src.models import AdapterConfig
from src.adapters import (
    HackerNewsAdapter,
    GitHubTrendingAdapter,
    RedditAdapter,
    WeiboAdapter,
    RSSAdapter,
)
from src.core import Aggregator


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


ADAPTER_MAP = {
    "hackernews": HackerNewsAdapter,
    "github_trending": GitHubTrendingAdapter,
    "reddit": RedditAdapter,
    "weibo": WeiboAdapter,
    "rss": RSSAdapter,
}


def get_default_configs() -> dict[str, AdapterConfig]:
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


async def run_adapters(configs: dict[str, AdapterConfig]) -> list:
    adapter_instances = []
    
    for name, config in configs.items():
        if not config.enabled:
            logger.info(f"Skipping disabled adapter: {name}")
            continue
        
        adapter_class = ADAPTER_MAP.get(name)
        if not adapter_class:
            logger.warning(f"No adapter found for: {name}")
            continue
        
        adapter = adapter_class(config)
        adapter_instances.append(adapter)
    
    adapter_instances.sort(key=lambda a: a.config.priority if a.config else 100)
    
    tasks = [adapter.run() for adapter in adapter_instances]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_items = []
    for adapter, result in zip(adapter_instances, results):
        if isinstance(result, Exception):
            logger.error(f"Adapter {adapter.name} failed: {result}")
        else:
            all_items.extend(result)
    
    return all_items


async def main():
    parser = argparse.ArgumentParser(description="HotBoard - World Hot Topics Aggregator")
    parser.add_argument("--output", "-o", default="data/hotboard.json", help="Output file path")
    parser.add_argument("--max-items", "-m", type=int, default=100, help="Maximum number of items")
    parser.add_argument("--adapters", "-a", nargs="+", help="Specific adapters to run")
    parser.add_argument("--log-level", "-l", default="INFO", help="Log level")
    args = parser.parse_args()
    
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    
    logger.info("Starting HotBoard scraper...")
    
    configs = get_default_configs()
    
    if args.adapters:
        for name in list(configs.keys()):
            if name not in args.adapters:
                configs[name].enabled = False
    
    items = await run_adapters(configs)
    
    logger.info(f"Total items collected: {len(items)}")
    
    aggregator = Aggregator(max_items=args.max_items)
    from src.models import HotItem
    items = aggregator.deduplicate(items)
    aggregator._calculate_scores(items)
    items.sort(key=lambda x: x.hot_score, reverse=True)
    items = items[:args.max_items]
    
    from src.models import HotBoard
    board = HotBoard()
    for item in items:
        board.add_item(item)
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(board.to_json())
    
    logger.info(f"Data saved to {output_path}")
    logger.info(f"Total sources: {len(board.sources)}")
    logger.info(f"Total items: {len(board.items)}")
    
    return board


if __name__ == "__main__":
    asyncio.run(main())
