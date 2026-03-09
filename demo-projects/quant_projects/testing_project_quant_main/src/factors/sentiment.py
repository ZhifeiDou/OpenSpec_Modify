"""Sentiment factor — time-decayed aggregation of LLM news sentiment scores."""
from __future__ import annotations

import json
import logging
import math
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from src.data.storage import DataStore
from src.factors.base import BaseFactor, register_factor

logger = logging.getLogger(__name__)


@register_factor
class SentimentFactor(BaseFactor):
    """Sentiment factor based on LLM-analyzed news sentiment scores."""

    name = "sentiment_score"
    category = "sentiment"

    def compute(
        self, universe: list[str], date: str, store: DataStore, config: dict
    ) -> pd.Series:
        """Compute sentiment factor for all stocks in the universe.

        Aggregates sentiment scores from related news using exponential
        time decay. Sector-level news applies to all stocks.
        """
        sentiment_cfg = config.get("sentiment", {})
        lookback_hours = sentiment_cfg.get("lookback_hours", 72)
        half_life_hours = sentiment_cfg.get("half_life_hours", 24)
        min_news_count = sentiment_cfg.get("min_news_count", 1)

        # Calculate time window
        try:
            ref_time = datetime.strptime(date, "%Y-%m-%d")
        except (ValueError, TypeError):
            ref_time = datetime.now()
        cutoff = ref_time - timedelta(hours=lookback_hours)
        cutoff_str = cutoff.isoformat()

        # Load news and sentiment data within the window
        news_df = store.read_news(since=cutoff_str)
        if news_df.empty:
            logger.info("No news in lookback window, all sentiment scores = 0")
            return pd.Series(0.0, index=universe)

        # Join with sentiment cache
        news_ids = news_df["id"].tolist()
        cache_df = store.read_sentiment_cache(news_ids=news_ids)
        if cache_df.empty:
            logger.info("No sentiment cache entries, all sentiment scores = 0")
            return pd.Series(0.0, index=universe)

        # Merge news with sentiment
        merged = news_df.merge(cache_df, left_on="id", right_on="news_id", how="inner")

        scores = {}
        for symbol in universe:
            score = self._compute_for_symbol(
                symbol, merged, ref_time, half_life_hours, min_news_count
            )
            scores[symbol] = score

        return pd.Series(scores)

    def _compute_for_symbol(
        self,
        symbol: str,
        merged: pd.DataFrame,
        ref_time: datetime,
        half_life_hours: float,
        min_news_count: int,
    ) -> float:
        """Compute time-decayed sentiment score for a single stock."""
        # Find news related to this symbol (stock-level) or sector-level
        relevant = merged[
            merged.apply(
                lambda row: self._is_relevant(row, symbol), axis=1
            )
        ]

        if len(relevant) < min_news_count:
            return 0.0

        total_weighted_score = 0.0
        total_weight = 0.0

        for _, row in relevant.iterrows():
            pub_time = self._parse_time(row.get("published_at", ""))
            if pub_time is None:
                continue

            hours_ago = (ref_time - pub_time).total_seconds() / 3600.0
            if hours_ago < 0:
                hours_ago = 0

            # Exponential decay: weight = exp(-ln(2) * hours / half_life)
            decay_weight = math.exp(-math.log(2) * hours_ago / half_life_hours)
            sentiment = float(row.get("sentiment_score", 0.0))

            total_weighted_score += sentiment * decay_weight
            total_weight += decay_weight

        if total_weight == 0:
            return 0.0

        return total_weighted_score / total_weight

    @staticmethod
    def _is_relevant(row: pd.Series, symbol: str) -> bool:
        """Check if a news item is relevant to the given symbol."""
        scope = row.get("scope", "sector")
        if scope == "sector":
            return True
        related_raw = row.get("related_symbols", "[]")
        try:
            related = json.loads(related_raw) if isinstance(related_raw, str) else related_raw
        except (json.JSONDecodeError, TypeError):
            related = []
        return symbol in related

    @staticmethod
    def _parse_time(time_str: str) -> datetime | None:
        """Parse various time string formats."""
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(time_str.strip(), fmt)
            except (ValueError, TypeError):
                continue
        return None
