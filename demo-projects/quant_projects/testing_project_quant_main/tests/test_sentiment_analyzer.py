"""Tests for LLM sentiment analyzer: parsing, caching, error handling."""
import json
import os
import tempfile
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from src.data.storage import DataStore
from src.sentiment.analyzer import SentimentAnalyzer


@pytest.fixture
def temp_store():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    store = DataStore(db_path=path)
    yield store
    try:
        os.unlink(path)
    except PermissionError:
        pass


@pytest.fixture
def analyzer_config():
    return {
        "data": {"db_path": "data/test.db"},
        "llm": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "api_key_env": "TEST_LLM_KEY",
            "batch_size": 5,
            "max_retries": 1,
            "temperature": 0.1,
        },
    }


def _insert_news(store, title="Test", published_at="2024-01-01 10:00:00"):
    """Helper to insert a news record and return its ID."""
    with store._get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO news (title, summary, published_at, source, related_symbols, scope, fetched_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, "summary", published_at, "test", "[]", "sector", "2024-01-01T11:00:00"),
        )
        return cursor.lastrowid


class TestPromptBuilding:
    """R2-UC1-S2: Verify prompt format for LLM batch analysis."""

    def test_build_prompt_format(self, analyzer_config, temp_store):
        analyzer = SentimentAnalyzer(analyzer_config, store=temp_store)
        _insert_news(temp_store, title="紫金矿业发现大型铜矿")
        _insert_news(temp_store, title="铜价暴跌创年内新低", published_at="2024-01-01 11:00:00")
        batch = temp_store.read_unanalyzed_news()
        prompt = analyzer._build_prompt(batch)
        assert "[0]" in prompt
        assert "[1]" in prompt
        assert "紫金矿业发现大型铜矿" in prompt
        assert "铜价暴跌创年内新低" in prompt


class TestLLMCall:
    """R2-UC1-S3, R2-UC1-E3a: LLM API call and retry logic."""

    def test_call_openai_success(self, analyzer_config, temp_store):
        """R2-UC1-S3: Successful OpenAI API call."""
        analyzer = SentimentAnalyzer(analyzer_config, store=temp_store)
        analyzer._api_key = "test-key"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps([
            {"index": 0, "classification": "bullish", "confidence": 0.85}
        ])

        mock_openai_mod = MagicMock()
        mock_openai_mod.OpenAI.return_value.chat.completions.create.return_value = mock_response
        with patch.dict("sys.modules", {"openai": mock_openai_mod}):
            result = analyzer._call_openai("test prompt")
        assert "bullish" in result

    def test_api_retry_on_failure(self, analyzer_config, temp_store):
        """R2-UC1-E3a: API call fails then succeeds on retry."""
        analyzer_config["llm"]["max_retries"] = 1
        analyzer = SentimentAnalyzer(analyzer_config, store=temp_store)
        analyzer._api_key = "test-key"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps([
            {"index": 0, "classification": "bullish", "confidence": 0.9}
        ])

        mock_openai_mod = MagicMock()
        mock_openai_mod.OpenAI.return_value.chat.completions.create.side_effect = [
            Exception("Connection timeout"),
            mock_response,
        ]
        with patch.dict("sys.modules", {"openai": mock_openai_mod}):
            with patch("time.sleep"):
                result = analyzer._call_llm("test prompt")
        assert result is not None
        assert "bullish" in result

    def test_all_retries_fail(self, analyzer_config, temp_store):
        """R2-UC1-E3a: All retries fail, returns None."""
        analyzer_config["llm"]["max_retries"] = 1
        analyzer = SentimentAnalyzer(analyzer_config, store=temp_store)
        analyzer._api_key = "test-key"

        mock_openai_mod = MagicMock()
        mock_openai_mod.OpenAI.return_value.chat.completions.create.side_effect = Exception("Server error")
        with patch.dict("sys.modules", {"openai": mock_openai_mod}):
            with patch("time.sleep"):
                result = analyzer._call_llm("test prompt")
        assert result is None


class TestResponseParsing:
    def test_parse_bullish(self, analyzer_config, temp_store):
        analyzer = SentimentAnalyzer(analyzer_config, store=temp_store)
        news_id = _insert_news(temp_store)
        batch = temp_store.read_unanalyzed_news()

        raw = json.dumps({"results": [
            {"index": 0, "classification": "bullish", "confidence": 0.85}
        ]})
        results = analyzer._parse_response(raw, batch)
        assert len(results) == 1
        assert results[0]["classification"] == "bullish"
        assert results[0]["sentiment_score"] == pytest.approx(0.85)

    def test_parse_bearish(self, analyzer_config, temp_store):
        analyzer = SentimentAnalyzer(analyzer_config, store=temp_store)
        _insert_news(temp_store)
        batch = temp_store.read_unanalyzed_news()

        raw = json.dumps([{"index": 0, "classification": "bearish", "confidence": 0.9}])
        results = analyzer._parse_response(raw, batch)
        assert results[0]["sentiment_score"] == pytest.approx(-0.9)

    def test_parse_invalid_json(self, analyzer_config, temp_store):
        analyzer = SentimentAnalyzer(analyzer_config, store=temp_store)
        _insert_news(temp_store)
        batch = temp_store.read_unanalyzed_news()

        results = analyzer._parse_response("not json at all", batch)
        assert len(results) == 1
        assert results[0]["sentiment_score"] == 0.0
        assert results[0]["classification"] == "neutral"

    def test_parse_missing_fields(self, analyzer_config, temp_store):
        analyzer = SentimentAnalyzer(analyzer_config, store=temp_store)
        _insert_news(temp_store)
        batch = temp_store.read_unanalyzed_news()

        raw = json.dumps([{"index": 0}])
        results = analyzer._parse_response(raw, batch)
        assert results[0]["classification"] == "neutral"
        assert results[0]["sentiment_score"] == 0.0


class TestCaching:
    def test_already_cached_skipped(self, analyzer_config, temp_store):
        news_id = _insert_news(temp_store)
        # Pre-populate cache
        with temp_store._get_conn() as conn:
            conn.execute(
                "INSERT INTO sentiment_cache (news_id, classification, confidence, sentiment_score, model_name, analyzed_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (news_id, "bullish", 0.8, 0.8, "test", "2024-01-01T12:00:00"),
            )
        unanalyzed = temp_store.read_unanalyzed_news()
        assert len(unanalyzed) == 0


class TestCacheSave:
    """R2-UC1-S6: Verify results are saved to sentiment_cache table."""

    def test_results_saved_to_cache(self, analyzer_config, temp_store):
        news_id = _insert_news(temp_store)
        analyzer = SentimentAnalyzer(analyzer_config, store=temp_store)
        results = [
            {
                "news_id": news_id,
                "classification": "bullish",
                "confidence": 0.85,
                "sentiment_score": 0.85,
                "model_name": "openai/gpt-4o-mini",
                "analyzed_at": "2024-01-01T12:00:00",
            }
        ]
        analyzer._save_results(results)
        cache = temp_store.read_sentiment_cache(news_ids=[news_id])
        assert len(cache) == 1
        assert cache.iloc[0]["classification"] == "bullish"
        assert cache.iloc[0]["sentiment_score"] == pytest.approx(0.85)


class TestAnalyzePending:
    """R2-UC1 Flow and R2-UC1-E1a: Full analysis pipeline tests."""

    def test_analyze_pending_full_flow(self, analyzer_config, temp_store):
        """R2-UC1: Full flow — insert news, mock LLM, verify cache populated."""
        _insert_news(temp_store, title="铜价暴涨利好矿企")
        analyzer = SentimentAnalyzer(analyzer_config, store=temp_store)
        analyzer._api_key = "test-key"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps([
            {"index": 0, "classification": "bullish", "confidence": 0.9}
        ])

        mock_openai_mod = MagicMock()
        mock_openai_mod.OpenAI.return_value.chat.completions.create.return_value = mock_response
        with patch.dict("sys.modules", {"openai": mock_openai_mod}):
            count = analyzer.analyze_pending()

        assert count == 1
        # Verify cache was written
        unanalyzed = temp_store.read_unanalyzed_news()
        assert len(unanalyzed) == 0

    def test_no_pending_news_skips(self, analyzer_config, temp_store):
        """R2-UC1-E1a: No pending news → skip LLM call, return 0."""
        analyzer = SentimentAnalyzer(analyzer_config, store=temp_store)
        analyzer._api_key = "test-key"
        result = analyzer.analyze_pending()
        assert result == 0


class TestGracefulDegradation:
    def test_no_api_key(self, analyzer_config, temp_store):
        with patch.dict(os.environ, {}, clear=True):
            analyzer = SentimentAnalyzer(analyzer_config, store=temp_store)
            _insert_news(temp_store)
            result = analyzer.analyze_pending()
            assert result == 0
