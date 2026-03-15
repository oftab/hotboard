from bs4 import BeautifulSoup
from typing import Optional
import feedparser
import json
import re


class Parser:
    @staticmethod
    def parse_html(html: str, selector: str) -> list[str]:
        soup = BeautifulSoup(html, "lxml")
        elements = soup.select(selector)
        return [elem.get_text(strip=True) for elem in elements]

    @staticmethod
    def parse_json(data: str | dict, path: str) -> list[dict]:
        if isinstance(data, str):
            data = json.loads(data)
        
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key, [])
            elif isinstance(current, list) and key.isdigit():
                idx = int(key)
                current = current[idx] if idx < len(current) else None
            else:
                return []
        
        if isinstance(current, list):
            return current
        return [current] if current else []

    @staticmethod
    def parse_rss(feed_url: str, raw_data: str) -> list[dict]:
        feed = feedparser.parse(raw_data)
        entries = []
        
        for entry in feed.entries:
            entries.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "url": entry.get("link", ""),
                "published": entry.get("published", ""),
                "tags": [tag.term for tag in entry.get("tags", [])],
            })
        
        return entries

    @staticmethod
    def extract_text(html: str, max_length: int = 200) -> str:
        soup = BeautifulSoup(html, "lxml")
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        return text[:max_length] + "..." if len(text) > max_length else text

    @staticmethod
    def extract_image_url(html: str) -> Optional[str]:
        soup = BeautifulSoup(html, "lxml")
        img = soup.find("img")
        if img and img.get("src"):
            return img.get("src")
        
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image.get("content")
        
        return None
