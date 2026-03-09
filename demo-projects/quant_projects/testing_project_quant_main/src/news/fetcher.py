"""Non-ferrous metals news fetcher using AKShare."""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timedelta

import pandas as pd

from src.data.storage import DataStore

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetch non-ferrous metals news from AKShare and persist to SQLite."""

    def __init__(self, config: dict, store: DataStore | None = None):
        self.config = config
        data_cfg = config.get("data", {})
        self.store = store or DataStore(data_cfg.get("db_path", "data/quant.db"))
        self.api_delay = data_cfg.get("api_delay_seconds", 0.5)

        news_cfg = config.get("news", {})
        self.keywords = news_cfg.get("keywords", ["有色金属"])
        self.lookback_hours = news_cfg.get("lookback_hours", 24)
        self.max_articles = news_cfg.get("max_articles", 50)

    def fetch_and_store(
        self, stock_names: dict[str, str] | None = None
    ) -> list[dict]:
        """Fetch latest news, deduplicate, associate with stocks, and store.

        Args:
            stock_names: {symbol: name} mapping from the universe for
                         associating news with individual stocks.

        Returns:
            List of newly stored news dicts.
        """
        raw_news = self._fetch_from_akshare()
        if not raw_news:
            return []

        # Associate with stocks
        if stock_names:
            for item in raw_news:
                related = self._match_stocks(item, stock_names)
                item["related_symbols"] = json.dumps(related, ensure_ascii=False)
                item["scope"] = "stock" if related else "sector"
        else:
            for item in raw_news:
                item["related_symbols"] = "[]"
                item["scope"] = "sector"

        # Deduplicate against existing news
        new_items = self._deduplicate(raw_news)
        if not new_items:
            logger.info("No new news articles to store")
            return []

        # Persist
        self._save_to_db(new_items)
        logger.info("Stored %d new news articles", len(new_items))
        return new_items

    def _fetch_from_akshare(self) -> list[dict]:
        """Call AKShare financial news API (optional dependency)."""
        try:
            import akshare as ak
        except ImportError:
            logger.warning(
                "akshare not installed — news fetching is unavailable. "
                "Install with: pip install akshare"
            )
            return []

        all_news = []
        cutoff = datetime.now() - timedelta(hours=self.lookback_hours)

        for keyword in self.keywords:
            try:
                df = ak.stock_news_em(symbol=keyword)
                if df is None or df.empty:
                    logger.info("No news found for keyword: %s", keyword)
                    continue

                for _, row in df.iterrows():
                    title = str(row.get("新闻标题", row.get("title", "")))
                    summary = str(row.get("新闻内容", row.get("content", "")))[:500]
                    pub_time = str(row.get("发布时间", row.get("datetime", "")))
                    source = str(row.get("文章来源", row.get("source", "")))

                    if not title:
                        continue

                    all_news.append({
                        "title": title,
                        "summary": summary,
                        "published_at": pub_time,
                        "source": source,
                        "fetched_at": datetime.now().isoformat(),
                    })

                time.sleep(self.api_delay)

            except Exception as e:
                logger.warning("Failed to fetch news for keyword '%s': %s", keyword, e)
                continue

        # Limit total articles
        return all_news[:self.max_articles]

    def _match_stocks(
        self, news_item: dict, stock_names: dict[str, str]
    ) -> list[str]:
        """Match news text against stock names/codes in the universe."""
        text = news_item.get("title", "") + " " + news_item.get("summary", "")
        matched = []
        for symbol, name in stock_names.items():
            if name in text or symbol in text:
                matched.append(symbol)
        return matched

    def _deduplicate(self, news_items: list[dict]) -> list[dict]:
        """Filter out news already in the database."""
        new_items = []
        with self.store._get_conn() as conn:
            for item in news_items:
                row = conn.execute(
                    "SELECT id FROM news WHERE title = ? AND published_at = ?",
                    (item["title"], item["published_at"]),
                ).fetchone()
                if row is None:
                    new_items.append(item)
        return new_items

    def _save_to_db(self, news_items: list[dict]):
        """Insert news into the news table."""
        with self.store._get_conn() as conn:
            for item in news_items:
                conn.execute(
                    "INSERT OR IGNORE INTO news "
                    "(title, summary, published_at, source, related_symbols, scope, fetched_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        item["title"],
                        item["summary"],
                        item["published_at"],
                        item["source"],
                        item.get("related_symbols", "[]"),
                        item.get("scope", "sector"),
                        item["fetched_at"],
                    ),
                )
