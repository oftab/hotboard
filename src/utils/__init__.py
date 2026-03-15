__all__ = ["generate_id", "format_timestamp", "truncate_text", "clean_html"]

import re
import hashlib
from datetime import datetime, timezone
from typing import Optional


def generate_id(content: str, max_length: int = 12) -> str:
    return hashlib.md5(content.encode()).hexdigest()[:max_length]


def format_timestamp(dt: Optional[datetime] = None, tz: Optional[timezone] = None) -> str:
    if dt is None:
        dt = datetime.now(tz or timezone.utc)
    return dt.isoformat()


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    if len(text) > max_length:
        return text[: max_length - len(suffix)] + suffix
    return text


def clean_html(html: str) -> str:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator=" ", strip=True)
