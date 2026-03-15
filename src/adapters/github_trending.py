from .base import BaseAdapter
from ..models import HotItem


class GitHubTrendingAdapter(BaseAdapter):
    name = "github_trending"
    platform = "github"
    
    API_URL = "https://api.github.com/repos/{owner}/{repo}"
    TRENDING_URL = "https://github.com/trending"
    
    LANGUAGES = ["", "python", "javascript", "rust", "go", "java", "typescript"]

    async def fetch(self) -> list[dict]:
        from ..core import Fetcher, Parser
        
        async with Fetcher(timeout=self.config.timeout if self.config else 30) as fetcher:
            repos = []
            
            for lang in self.LANGUAGES[:3]:
                url = f"https://api.github.com/repos/search/repositories"
                params = {
                    "q": f"stars:>1" + (f" language:{lang}" if lang else ""),
                    "sort": "stars",
                    "order": "desc",
                    "per_page": self.config.max_items if self.config else 10,
                }
                
                try:
                    response = await fetcher.get(url, params=params)
                    if response and response.status_code == 200:
                        data = response.json()
                        repos.extend(data.get("items", []))
                except Exception as e:
                    self.logger.warning(f"Error fetching {lang}: {e}")
            
            return repos[: self.config.max_items if self.config else 20]

    def parse(self, raw_data: list[dict]) -> list[HotItem]:
        items = []
        
        for repo in raw_data:
            if not repo:
                continue
            
            title = repo.get("full_name", "")
            url = repo.get("html_url", "")
            description = repo.get("description", "") or ""
            stars = repo.get("stargazers_count", 0) or 0
            forks = repo.get("forks_count", 0) or 0
            language = repo.get("language", "") or ""
            
            hot_score = stars + forks * 0.5
            
            summary = f"⭐ {stars:,} | 🍴 {forks:,}" + (f" | {language}" if language else "")
            
            items.append(
                self._create_hot_item(
                    title=title,
                    url=url,
                    summary=description or summary,
                    hot_score=hot_score,
                    category="tech",
                    tags=["github", "trending", "opensource", language.lower()] if language else ["github", "trending", "opensource"],
                )
            )
        
        return items
