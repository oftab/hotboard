import asyncio
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="HotBoard - World Hot Topics Aggregator")
    parser.add_argument("--output", "-o", default="hotboard.json", help="Output file path")
    parser.add_argument("--max-items", "-m", type=int, default=100, help="Maximum number of items")
    parser.add_argument("--log-level", "-l", default="INFO", help="Log level")
    args = parser.parse_args()

    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    logger.info("Starting HotBoard scraper...")

    from src.models import HotItem, HotBoard
    from src.adapters import (
        HackerNewsAdapter, GitHubTrendingAdapter, RedditAdapter, WeiboAdapter, RSSAdapter,
        ZhihuAdapter, BilibiliAdapter, DouyinAdapter, DoubanAdapter, TiebaAdapter,
        ToutiaoAdapter, BaiduAdapter, ProductHuntAdapter, DevToAdapter, DiggAdapter,
        WeixinAdapter, V2exAdapter, JuejinAdapter
    )
    from src.models import AdapterConfig
    from src.core import Aggregator

    configs = {
        "hackernews": AdapterConfig(name="hackernews", enabled=True, priority=10, category="tech"),
        "github_trending": AdapterConfig(name="github_trending", enabled=True, priority=20, category="tech"),
        "reddit": AdapterConfig(name="reddit", enabled=True, priority=30, category="social"),
        "weibo": AdapterConfig(name="weibo", enabled=True, priority=40, category="social"),
        "zhihu": AdapterConfig(name="zhihu", enabled=True, priority=45, category="social"),
        "bilibili": AdapterConfig(name="bilibili", enabled=True, priority=50, category="entertainment"),
        "douyin": AdapterConfig(name="douyin", enabled=True, priority=55, category="entertainment"),
        "douban": AdapterConfig(name="douban", enabled=True, priority=60, category="entertainment"),
        "tieba": AdapterConfig(name="tieba", enabled=True, priority=65, category="social"),
        "toutiao": AdapterConfig(name="toutiao", enabled=True, priority=70, category="news"),
        "baidu": AdapterConfig(name="baidu", enabled=True, priority=75, category="news"),
        "producthunt": AdapterConfig(name="producthunt", enabled=True, priority=80, category="tech"),
        "devto": AdapterConfig(name="devto", enabled=True, priority=85, category="tech"),
        "digg": AdapterConfig(name="digg", enabled=True, priority=90, category="news"),
        "weixin": AdapterConfig(name="weixin", enabled=True, priority=95, category="social"),
        "v2ex": AdapterConfig(name="v2ex", enabled=True, priority=100, category="tech"),
        "juejin": AdapterConfig(name="juejin", enabled=True, priority=105, category="tech"),
        "rss": AdapterConfig(
            name="rss", 
            enabled=True, 
            priority=110, 
            category="news",
            rss_urls=[
                "https://feeds.bbci.co.uk/news/world/rss.xml",
                "https://www.reutersagency.com/feed/?best-topics=tech",
            ]
        ),
    }

    adapters = [
        HackerNewsAdapter(configs["hackernews"]),
        GitHubTrendingAdapter(configs["github_trending"]),
        RedditAdapter(configs["reddit"]),
        WeiboAdapter(configs["weibo"]),
        ZhihuAdapter(configs["zhihu"]),
        BilibiliAdapter(configs["bilibili"]),
        DouyinAdapter(configs["douyin"]),
        DoubanAdapter(configs["douban"]),
        TiebaAdapter(configs["tieba"]),
        ToutiaoAdapter(configs["toutiao"]),
        BaiduAdapter(configs["baidu"]),
        ProductHuntAdapter(configs["producthunt"]),
        DevToAdapter(configs["devto"]),
        DiggAdapter(configs["digg"]),
        WeixinAdapter(configs["weixin"]),
        V2exAdapter(configs["v2ex"]),
        JuejinAdapter(configs["juejin"]),
        RSSAdapter(configs["rss"]),
    ]

    all_items = []
    for adapter in adapters:
        try:
            items = await adapter.run()
            logger.info(f"{adapter.name}: fetched {len(items)} items")
            all_items.extend(items)
        except Exception as e:
            logger.error(f"{adapter.name} failed: {e}")

    logger.info(f"Total items collected: {len(all_items)}")

    aggregator = Aggregator(max_items=args.max_items)
    all_items = aggregator.deduplicate(all_items)
    aggregator._calculate_scores(all_items)
    all_items.sort(key=lambda x: x.hot_score, reverse=True)
    all_items = all_items[:args.max_items]

    board = HotBoard()
    for item in all_items:
        board.add_item(item)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(board.to_json())

    logger.info(f"Data saved to {output_path}")
    logger.info(f"Sources: {board.sources}")
    logger.info(f"Total items: {len(board.items)}")

    return board


if __name__ == "__main__":
    asyncio.run(main())
