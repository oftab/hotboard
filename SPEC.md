# HotBoard - 世界热点聚合抓取项目

## 1. 项目概述

**项目名称**: HotBoard (热榜聚合器)  
**项目类型**: 自动化的世界热点内容聚合与展示系统  
**核心功能**: 定时从全球主流社交媒体、新闻平台、技术社区抓取热门内容，聚合后通过GitHub Pages展示  
**目标用户**: 关注全球热点资讯的技术人员、内容创作者、新闻爱好者

## 2. 技术架构

### 2.1 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 爬虫引擎 | [Crawl4AI](https://github.com/unclecode/crawl4ai) | AI驱动的网页爬虫，支持LLM辅助提取 |
| RSS解析 | feedparser | 标准RSS/Atom feed解析 |
| 文章提取 | newspaper3k | 新闻文章内容提取 |
| HTTP客户端 | httpx | 现代化异步HTTP客户端 |
| 任务调度 | GitHub Actions | 定时触发抓取任务 |
| 静态展示 | GitHub Pages + Vanilla JS | 无需后端的纯静态展示 |

### 2.2 架构模式

采用**插件化适配器模式** + **责任链模式**：

```
┌─────────────────────────────────────────────────────┐
│                   Scheduler                         │
│              (GitHub Actions)                        │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                  Core Engine                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  Fetcher    │  │  Parser     │  │ Aggregator  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Adapter    │  │  Adapter    │  │  Adapter    │
│  (HackerNo) │  │  (Twitter)  │  │  (Weibo)    │
└─────────────┘  └─────────────┘  └─────────────┘
```

## 3. 功能规范

### 3.1 支持平台

| 类别 | 平台 | 优先级 | 抓取内容 |
|------|------|--------|----------|
| 技术社区 | Hacker News | P0 | 热门文章、讨论 |
| 技术社区 | GitHub Trending | P0 | 热门开源项目 |
| 技术社区 | Reddit | P0 | 热帖、subreddit |
| 社交媒体 | X (Twitter) | P1 | 热门话题、趋势 |
| 社交媒体 | Weibo | P1 | 热搜榜 |
| 新闻媒体 | Reuters | P1 | 要闻 |
| 新闻媒体 | BBC | P1 | 要闻 |
| 新闻媒体 | CNN | P2 | 要闻 |
| 聚合器 | RSS Feeds | P1 | 自定义订阅源 |

### 3.2 数据模型

```typescript
interface HotItem {
  id: string;                    // 唯一标识
  title: string;                 // 标题
  summary: string;               // 摘要
  url: string;                   // 原文链接
  imageUrl?: string;             // 封面图
  source: string;                // 来源平台
  sourceIcon?: string;           // 来源图标
  hotScore: number;              # 热度分数
  category: string;              // 分类
  publishedAt: string;           // 发布时间 (ISO8601)
  fetchedAt: string;             # 抓取时间 (ISO8601)
  tags?: string[];               # 标签
}

interface HotBoard {
  version: string;               // 数据版本
  generatedAt: string;           # 生成时间
  items: HotItem[];              # 热点列表
  sources: string[];             # 数据来源列表
}
```

### 3.3 核心功能

1. **定时抓取**: 每日UTC 0点、6点、12点、18点自动执行
2. **多源聚合**: 并发抓取所有启用的平台
3. **去重排序**: 基于热度和时间排序
4. **统一输出**: 生成标准化的JSON数据
5. **静态展示**: GitHub Pages页面展示

## 4. 目录结构

```
hotboard/
├── .github/
│   └── workflows/
│       └── scrape.yml           # 定时抓取工作流
├── src/
│   ├── adapters/                # 平台适配器
│   │   ├── __init__.py
│   │   ├── base.py              # 适配器基类
│   │   ├── hackernews.py        # Hacker News
│   │   ├── github_trending.py   # GitHub Trending
│   │   ├── reddit.py            # Reddit
│   │   ├── twitter.py           # X/Twitter
│   │   ├── weibo.py             # 微博
│   │   └── rss.py               # RSS聚合
│   ├── core/                    # 核心引擎
│   │   ├── __init__.py
│   │   ├── fetcher.py           # HTTP请求封装
│   │   ├── parser.py            # 内容解析
│   │   └── aggregator.py       # 数据聚合
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   └── hot_item.py          # HotItem模型
│   ├── config/                  # 配置
│   │   ├── __init__.py
│   │   └── settings.py         # 配置项
│   └── main.py                  # 入口文件
├── web/                         # GitHub Pages展示
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── data/                        # 抓取数据输出
│   └── hotboard.json           # 聚合结果
├── config.yaml                  # 平台配置
├── requirements.txt             # Python依赖
├── pyproject.toml              # 项目配置
└── README.md                   # 项目说明
```

## 5. 适配器规范

每个适配器需继承基类并实现以下接口：

```python
class BaseAdapter(ABC):
    name: str           # 适配器名称
    platform: str      # 平台标识
    priority: int      # 优先级
    
    @abstractmethod
    async def fetch(self) -> List[HotItem]:
        """抓取热点数据"""
        pass
    
    @abstractmethod
    def parse(self, raw_data) -> List[HotItem]:
        """解析原始数据"""
        pass
    
    async def run(self) -> List[HotItem]:
        """执行完整抓取流程"""
        raw = await self.fetch()
        return self.parse(raw)
```

## 6. GitHub Actions 工作流

```yaml
on:
  schedule:
    - cron: '0 0,6,12,18 * * *'  # 每日0、6、12、18点UTC
  workflow_dispatch:             # 支持手动触发

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run scraper
        run: python src/main.py
      - name: Commit and push
        run: |
          git config user.name "HotBoard Bot"
          git add data/hotboard.json
          git commit -m "Update hotboard data"
          git push
```

## 7. 验收标准

- [ ] 项目能正常部署到GitHub
- [ ] GitHub Actions定时任务按计划执行
- [ ] 至少支持5个主流平台的热点抓取
- [ ] 生成标准化的JSON数据
- [ ] GitHub Pages能展示热点内容
- [ ] 代码遵循PEP 8规范
- [ ] 具备良好的错误处理和日志记录
- [ ] 支持通过配置文件启用/禁用平台

## 8. 参考资源

- [Crawl4AI](https://github.com/unclecode/crawl4ai) - AI爬虫
- [feedparser](https://github.com/kurtmckee/feedparser) - RSS解析
- [newspaper3k](https://github.com/codelucas/newspaper) - 文章提取
- [httpx](https://www.python-httpx.org/) - 异步HTTP
