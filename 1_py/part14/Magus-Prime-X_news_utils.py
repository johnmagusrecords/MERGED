import json
from typing import List
from news_monitor import NewsArticle


def export_news_to_json(articles: List[NewsArticle], filepath: str) -> None:
    """Export a list of NewsArticle objects to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump([a.__dict__ for a in articles],
                  f, ensure_ascii=False, indent=2)
