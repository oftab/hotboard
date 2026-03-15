import asyncio
import argparse
import logging
import sys
import json
import hashlib
import traceback
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def generate_item_hash(title: str, url: str) -> str:
    content = f"{title}|{url}"
    return hashlib.md5(content.encode()).hexdigest()


def load_history(history_dir: Path, days: int = 7) -> dict:
    history = {}
    if not history_dir.exists():
        return history
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    for history_file in history_dir.glob("*.json"):
        try:
            file_date_str = history_file.stem
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            
            if file_date < cutoff_date:
                continue
            
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("items", []):
                    item_hash = generate_item_hash(item.get("title", ""), item.get("url", ""))
                    if item_hash not in history or item.get("hot_score", 0) > history[item_hash].get("hot_score", 0):
                        history[item_hash] = item
        except Exception as e:
            logger.warning(f"Error loading history file {history_file}: {e}")
    
    return history


def save_to_history(output_path: Path, history_dir: Path):
    if not output_path.exists():
        return
    
    history_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    history_file = history_dir / f"{today}.json"
    
    with open(output_path, "r", encoding="utf-8") as f:
        current_data = json.load(f)
    
    if history_file.exists():
        with open(history_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        
        existing_hashes = {}
        for i, item in enumerate(existing_data.get("items", [])):
            item_hash = generate_item_hash(item.get("title", ""), item.get("url", ""))
            existing_hashes[item_hash] = i
        
        merged_items = existing_data.get("items", []).copy()
        
        for item in current_data.get("items", []):
            item_hash = generate_item_hash(item.get("title", ""), item.get("url", ""))
            if item_hash in existing_hashes:
                idx = existing_hashes[item_hash]
                if item.get("hot_score", 0) > merged_items[idx].get("hot_score", 0):
                    merged_items[idx] = item
            else:
                merged_items.append(item)
        
        merged_items.sort(key=lambda x: x.get("hot_score", 0), reverse=True)
        
        current_data = {
            "version": existing_data.get("version", "1.0"),
            "generatedAt": current_data.get("generatedAt"),
            "items": merged_items,
            "sources": list(set(existing_data.get("sources", []) + current_data.get("sources", [])))
        }
    
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(current_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"History saved to {history_file}, total items: {len(current_data.get('items', []))}")


def filter_today_items(items: list) -> list:
    return items


async def main():
    parser = argparse.ArgumentParser(description="HotBoard - World Hot Topics Aggregator")
    parser.add_argument("--output", "-o", default="hotboard.json", help="Output file path")
    parser.add_argument("--max-items", "-m", type=int, default=0, help="Maximum number of items (0 = no limit)")
    parser.add_argument("--log-level", "-l", default="INFO", help="Log level")
    parser.add_argument("--history-dir", default="history", help="History directory")
    parser.add_argument("--include-history", action="store_true", help="Include historical items")
    parser.add_argument("--today-only", action="store_true", default=False, help="Only include today's items")
    args = parser.parse_args()

    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    logger.info("Starting HotBoard scraper...")

    from src.models import HotItem, HotBoard
    from src.adapters import (
        HackerNewsAdapter, GitHubTrendingAdapter, RedditAdapter, WeiboAdapter, RSSAdapter,
        ZhihuAdapter, BilibiliAdapter, DouyinAdapter, DoubanAdapter, TiebaAdapter,
        ToutiaoAdapter, BaiduAdapter, ProductHuntAdapter, DevToAdapter, DiggAdapter,
        WeixinAdapter, V2exAdapter, JuejinAdapter, KuaishouAdapter, XiaohongshuAdapter,
        Kr36Adapter, HuxiuAdapter, ITHomeAdapter, ThepaperAdapter, NetEaseAdapter,
        SspaiAdapter, CoolapkAdapter, ZhihuDailyAdapter, WeiboHotAdapter, DingxiangAdapter,
        SinaAdapter, SohuAdapter, ZolAdapter, LanjingerAdapter, TmtPostAdapter,
        WallstreetcnAdapter, IfengAdapter, CaixinAdapter, InfoQAdapter, SegmentfaultAdapter,
        CsdnAdapter, OschinaAdapter,
        NgaAdapter, HupuAdapter, PojieAdapter, GuokrAdapter, JianshuAdapter,
        HellogithubAdapter, IfanrAdapter, DoubanGroupAdapter, QqnewsAdapter,
        MiyousheAdapter, WereadAdapter, HostlocAdapter, NodeseekAdapter, Ct51Adapter
    )
    from src.models import AdapterConfig
    from src.core import Aggregator

    configs = {
        "hackernews": AdapterConfig(name="hackernews", enabled=True, priority=10, category="tech"),
        "github_trending": AdapterConfig(name="github_trending", enabled=True, priority=20, category="tech"),
        "reddit": AdapterConfig(name="reddit", enabled=True, priority=30, category="social"),
        "weibo": AdapterConfig(name="weibo", enabled=True, priority=40, category="social"),
        "weibo_hot": AdapterConfig(name="weibo_hot", enabled=True, priority=41, category="social"),
        "zhihu": AdapterConfig(name="zhihu", enabled=True, priority=45, category="social"),
        "zhihu_daily": AdapterConfig(name="zhihu_daily", enabled=True, priority=46, category="social"),
        "bilibili": AdapterConfig(name="bilibili", enabled=True, priority=50, category="entertainment"),
        "douyin": AdapterConfig(name="douyin", enabled=True, priority=55, category="entertainment"),
        "kuaishou": AdapterConfig(name="kuaishou", enabled=True, priority=56, category="entertainment"),
        "xiaohongshu": AdapterConfig(name="xiaohongshu", enabled=True, priority=57, category="entertainment"),
        "douban": AdapterConfig(name="douban", enabled=True, priority=60, category="entertainment"),
        "tieba": AdapterConfig(name="tieba", enabled=True, priority=65, category="social"),
        "toutiao": AdapterConfig(name="toutiao", enabled=True, priority=70, category="news"),
        "baidu": AdapterConfig(name="baidu", enabled=True, priority=75, category="news"),
        "thepaper": AdapterConfig(name="thepaper", enabled=True, priority=76, category="news"),
        "netease": AdapterConfig(name="netease", enabled=True, priority=77, category="news"),
        "sina": AdapterConfig(name="sina", enabled=True, priority=78, category="news"),
        "sohu": AdapterConfig(name="sohu", enabled=True, priority=79, category="news"),
        "ifeng": AdapterConfig(name="ifeng", enabled=True, priority=80, category="news"),
        "producthunt": AdapterConfig(name="producthunt", enabled=True, priority=85, category="tech"),
        "devto": AdapterConfig(name="devto", enabled=True, priority=90, category="tech"),
        "digg": AdapterConfig(name="digg", enabled=True, priority=95, category="news"),
        "weixin": AdapterConfig(name="weixin", enabled=True, priority=100, category="social"),
        "v2ex": AdapterConfig(name="v2ex", enabled=True, priority=105, category="tech"),
        "juejin": AdapterConfig(name="juejin", enabled=True, priority=110, category="tech"),
        "kr36": AdapterConfig(name="kr36", enabled=True, priority=115, category="tech"),
        "huxiu": AdapterConfig(name="huxiu", enabled=True, priority=120, category="tech"),
        "ithome": AdapterConfig(name="ithome", enabled=True, priority=125, category="tech"),
        "sspai": AdapterConfig(name="sspai", enabled=True, priority=130, category="tech"),
        "coolapk": AdapterConfig(name="coolapk", enabled=True, priority=135, category="tech"),
        "zol": AdapterConfig(name="zol", enabled=True, priority=140, category="tech"),
        "lanjinger": AdapterConfig(name="lanjinger", enabled=True, priority=145, category="finance"),
        "tmtpost": AdapterConfig(name="tmtpost", enabled=True, priority=150, category="tech"),
        "wallstreetcn": AdapterConfig(name="wallstreetcn", enabled=True, priority=155, category="finance"),
        "caixin": AdapterConfig(name="caixin", enabled=True, priority=160, category="finance"),
        "dingxiang": AdapterConfig(name="dingxiang", enabled=True, priority=165, category="health"),
        "infoq": AdapterConfig(name="infoq", enabled=True, priority=170, category="tech"),
        "segmentfault": AdapterConfig(name="segmentfault", enabled=True, priority=175, category="tech"),
        "csdn": AdapterConfig(name="csdn", enabled=True, priority=180, category="tech"),
        "oschina": AdapterConfig(name="oschina", enabled=True, priority=185, category="tech"),
        "nga": AdapterConfig(name="nga", enabled=True, priority=186, category="social"),
        "hupu": AdapterConfig(name="hupu", enabled=True, priority=187, category="social"),
        "52pojie": AdapterConfig(name="52pojie", enabled=True, priority=188, category="tech"),
        "guokr": AdapterConfig(name="guokr", enabled=True, priority=189, category="tech"),
        "jianshu": AdapterConfig(name="jianshu", enabled=True, priority=190, category="tech"),
        "hellogithub": AdapterConfig(name="hellogithub", enabled=True, priority=191, category="tech"),
        "ifanr": AdapterConfig(name="ifanr", enabled=True, priority=192, category="tech"),
        "douban_group": AdapterConfig(name="douban_group", enabled=True, priority=193, category="social"),
        "qqnews": AdapterConfig(name="qqnews", enabled=True, priority=194, category="news"),
        "miyoushe": AdapterConfig(name="miyoushe", enabled=True, priority=195, category="entertainment"),
        "weread": AdapterConfig(name="weread", enabled=True, priority=196, category="entertainment"),
        "hostloc": AdapterConfig(name="hostloc", enabled=True, priority=197, category="tech"),
        "nodeseek": AdapterConfig(name="nodeseek", enabled=True, priority=198, category="tech"),
        "51cto": AdapterConfig(name="51cto", enabled=True, priority=199, category="tech"),
        "rss": AdapterConfig(
            name="rss", 
            enabled=True, 
            priority=190, 
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
        WeiboHotAdapter(configs["weibo_hot"]),
        ZhihuAdapter(configs["zhihu"]),
        ZhihuDailyAdapter(configs["zhihu_daily"]),
        BilibiliAdapter(configs["bilibili"]),
        DouyinAdapter(configs["douyin"]),
        KuaishouAdapter(configs["kuaishou"]),
        XiaohongshuAdapter(configs["xiaohongshu"]),
        DoubanAdapter(configs["douban"]),
        TiebaAdapter(configs["tieba"]),
        ToutiaoAdapter(configs["toutiao"]),
        BaiduAdapter(configs["baidu"]),
        ThepaperAdapter(configs["thepaper"]),
        NetEaseAdapter(configs["netease"]),
        SinaAdapter(configs["sina"]),
        SohuAdapter(configs["sohu"]),
        IfengAdapter(configs["ifeng"]),
        ProductHuntAdapter(configs["producthunt"]),
        DevToAdapter(configs["devto"]),
        DiggAdapter(configs["digg"]),
        WeixinAdapter(configs["weixin"]),
        V2exAdapter(configs["v2ex"]),
        JuejinAdapter(configs["juejin"]),
        Kr36Adapter(configs["kr36"]),
        HuxiuAdapter(configs["huxiu"]),
        ITHomeAdapter(configs["ithome"]),
        SspaiAdapter(configs["sspai"]),
        CoolapkAdapter(configs["coolapk"]),
        ZolAdapter(configs["zol"]),
        LanjingerAdapter(configs["lanjinger"]),
        TmtPostAdapter(configs["tmtpost"]),
        WallstreetcnAdapter(configs["wallstreetcn"]),
        CaixinAdapter(configs["caixin"]),
        DingxiangAdapter(configs["dingxiang"]),
        InfoQAdapter(configs["infoq"]),
        SegmentfaultAdapter(configs["segmentfault"]),
        CsdnAdapter(configs["csdn"]),
        OschinaAdapter(configs["oschina"]),
        NgaAdapter(configs["nga"]),
        HupuAdapter(configs["hupu"]),
        PojieAdapter(configs["52pojie"]),
        GuokrAdapter(configs["guokr"]),
        JianshuAdapter(configs["jianshu"]),
        HellogithubAdapter(configs["hellogithub"]),
        IfanrAdapter(configs["ifanr"]),
        DoubanGroupAdapter(configs["douban_group"]),
        QqnewsAdapter(configs["qqnews"]),
        MiyousheAdapter(configs["miyoushe"]),
        WereadAdapter(configs["weread"]),
        HostlocAdapter(configs["hostloc"]),
        NodeseekAdapter(configs["nodeseek"]),
        Ct51Adapter(configs["51cto"]),
        RSSAdapter(configs["rss"]),
    ]

    all_items = []
    success_count = 0
    failed_count = 0
    failed_adapters = []
    
    for adapter in adapters:
        try:
            items = await adapter.run()
            logger.info(f"✓ {adapter.name}: fetched {len(items)} items")
            all_items.extend(items)
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_adapters.append(adapter.name)
            logger.error(f"✗ {adapter.name} failed: {e}")
            logger.debug(f"Traceback for {adapter.name}:\n{traceback.format_exc()}")

    logger.info(f"Total items collected: {len(all_items)}")
    logger.info(f"Adapters summary: {success_count} succeeded, {failed_count} failed")
    
    if failed_adapters:
        logger.warning(f"Failed adapters: {', '.join(failed_adapters)}")

    output_path = Path(args.output)
    history_dir = Path(args.history_dir)
    
    history = load_history(history_dir)
    logger.info(f"Loaded {len(history)} historical items")

    aggregator = Aggregator(max_items=args.max_items if args.max_items > 0 else len(all_items))
    all_items = aggregator.deduplicate(all_items)
    aggregator._calculate_scores(all_items)
    
    all_items.sort(key=lambda x: x.hot_score, reverse=True)
    
    if args.max_items > 0:
        all_items = all_items[:args.max_items]

    board = HotBoard()
    for item in all_items:
        board.add_item(item)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(board.to_json())

    logger.info(f"Data saved to {output_path}")
    logger.info(f"Sources: {board.sources}")
    logger.info(f"Total items: {len(board.items)}")

    save_to_history(output_path, history_dir)

    return board


if __name__ == "__main__":
    asyncio.run(main())
