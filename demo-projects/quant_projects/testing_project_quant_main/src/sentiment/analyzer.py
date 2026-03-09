"""LLM-based news sentiment analyzer with caching and graceful degradation."""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime

import pandas as pd

from src.data.storage import DataStore

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "你是一个专业的有色金属行业分析师。分析以下新闻对有色金属板块/个股的影响。\n"
    "对每条新闻，判断其对股价的影响方向并给出置信度。\n"
    "返回 JSON 数组，每个元素包含：\n"
    '  - "index": 新闻序号 (从0开始)\n'
    '  - "classification": "bullish"(利多) / "bearish"(利空) / "neutral"(中性)\n'
    '  - "confidence": 0.0-1.0 的置信度\n'
    "只返回 JSON，不要其他文字。"
)


class SentimentAnalyzer:
    """Analyze news sentiment using LLM API with caching."""

    def __init__(self, config: dict, store: DataStore | None = None):
        self.config = config
        data_cfg = config.get("data", {})
        self.store = store or DataStore(data_cfg.get("db_path", "data/quant.db"))

        llm_cfg = config.get("llm", {})
        self.provider = llm_cfg.get("provider", "openai")
        self.model = llm_cfg.get("model", "gpt-4o-mini")
        self.api_key_env = llm_cfg.get("api_key_env", "OPENAI_API_KEY")
        self.batch_size = llm_cfg.get("batch_size", 10)
        self.max_retries = llm_cfg.get("max_retries", 2)
        self.temperature = llm_cfg.get("temperature", 0.1)

        self._api_key = os.environ.get(self.api_key_env)

    def analyze_pending(self) -> int:
        """Analyze all unanalyzed news. Returns count of newly analyzed items."""
        if not self._api_key:
            logger.warning(
                "LLM API key not configured (env: %s), sentiment analysis disabled",
                self.api_key_env,
            )
            return 0

        pending = self.store.read_unanalyzed_news()
        if pending.empty:
            logger.info("No pending news to analyze")
            return 0

        total_analyzed = 0
        for batch_start in range(0, len(pending), self.batch_size):
            batch = pending.iloc[batch_start : batch_start + self.batch_size]
            results = self._analyze_batch(batch)
            if results:
                self._save_results(results)
                total_analyzed += len(results)

        logger.info("Analyzed %d news articles", total_analyzed)
        return total_analyzed

    def _analyze_batch(self, batch: pd.DataFrame) -> list[dict]:
        """Send a batch of news to LLM and parse results."""
        news_text = self._build_prompt(batch)
        raw_response = self._call_llm(news_text)
        if raw_response is None:
            return []
        return self._parse_response(raw_response, batch)

    def _build_prompt(self, batch: pd.DataFrame) -> str:
        """Build the user prompt with numbered news items."""
        lines = []
        for i, (_, row) in enumerate(batch.iterrows()):
            title = row.get("title", "")
            summary = row.get("summary", "")
            lines.append(f"[{i}] 标题: {title}")
            if summary:
                lines.append(f"    摘要: {summary[:200]}")
        return "\n".join(lines)

    def _call_llm(self, user_message: str) -> str | None:
        """Call LLM API with retry logic."""
        for attempt in range(1 + self.max_retries):
            try:
                if self.provider == "anthropic":
                    return self._call_anthropic(user_message)
                else:
                    return self._call_openai(user_message)
            except Exception as e:
                wait = 2**attempt
                if attempt < self.max_retries:
                    logger.warning(
                        "LLM API call failed (attempt %d/%d): %s, retrying in %ds",
                        attempt + 1, 1 + self.max_retries, e, wait,
                    )
                    time.sleep(wait)
                else:
                    logger.warning(
                        "LLM API call failed after %d attempts: %s, skipping batch",
                        1 + self.max_retries, e,
                    )
        return None

    def _call_openai(self, user_message: str) -> str:
        """Call OpenAI API."""
        from openai import OpenAI

        client = OpenAI(api_key=self._api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content

    def _call_anthropic(self, user_message: str) -> str:
        """Call Anthropic API."""
        from anthropic import Anthropic

        client = Anthropic(api_key=self._api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            temperature=self.temperature,
        )
        return response.content[0].text

    def _parse_response(
        self, raw: str, batch: pd.DataFrame
    ) -> list[dict]:
        """Parse LLM JSON response into sentiment results."""
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("LLM returned invalid JSON, marking batch as neutral")
            return self._neutral_results(batch)

        # Handle both {"results": [...]} and direct [...] formats
        if isinstance(parsed, dict):
            items = parsed.get("results", parsed.get("data", []))
            if not isinstance(items, list):
                items = list(parsed.values())
                if items and isinstance(items[0], list):
                    items = items[0]
        elif isinstance(parsed, list):
            items = parsed
        else:
            logger.warning("LLM returned unexpected format, marking batch as neutral")
            return self._neutral_results(batch)

        results = []
        news_ids = batch["id"].tolist()
        now = datetime.now().isoformat()

        for i, news_id in enumerate(news_ids):
            if i < len(items) and isinstance(items[i], dict):
                item = items[i]
                classification = item.get("classification", "neutral")
                confidence = float(item.get("confidence", 0.0))

                if classification not in ("bullish", "bearish", "neutral"):
                    classification = "neutral"
                confidence = max(0.0, min(1.0, confidence))

                if classification == "bullish":
                    score = confidence
                elif classification == "bearish":
                    score = -confidence
                else:
                    score = 0.0
            else:
                classification = "neutral"
                confidence = 0.0
                score = 0.0

            results.append({
                "news_id": news_id,
                "classification": classification,
                "confidence": confidence,
                "sentiment_score": score,
                "model_name": f"{self.provider}/{self.model}",
                "analyzed_at": now,
            })

        return results

    def _neutral_results(self, batch: pd.DataFrame) -> list[dict]:
        """Generate neutral results for a batch (fallback on parse failure)."""
        now = datetime.now().isoformat()
        return [
            {
                "news_id": row["id"],
                "classification": "neutral",
                "confidence": 0.0,
                "sentiment_score": 0.0,
                "model_name": f"{self.provider}/{self.model}",
                "analyzed_at": now,
            }
            for _, row in batch.iterrows()
        ]

    def _save_results(self, results: list[dict]):
        """Write sentiment results to sentiment_cache table."""
        with self.store._get_conn() as conn:
            for r in results:
                conn.execute(
                    "INSERT OR REPLACE INTO sentiment_cache "
                    "(news_id, classification, confidence, sentiment_score, model_name, analyzed_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        r["news_id"],
                        r["classification"],
                        r["confidence"],
                        r["sentiment_score"],
                        r["model_name"],
                        r["analyzed_at"],
                    ),
                )
