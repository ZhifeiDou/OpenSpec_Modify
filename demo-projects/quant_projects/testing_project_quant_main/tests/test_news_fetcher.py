"""Tests for news fetcher: deduplication, stock association, persistence."""
import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from src.data.storage import DataStore
from src.news.fetcher import NewsFetcher


@pytest.fixture
def temp_store():
    """Create a temporary DataStore for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    store = DataStore(db_path=path)
    yield store
    try:
        os.unlink(path)
    except PermissionError:
        pass


@pytest.fixture
def fetcher_config():
    return {
        "data": {"db_path": "data/test.db", "api_delay_seconds": 0},
        "news": {"keywords": ["有色金属"], "lookback_hours": 24, "max_articles": 50},
    }


class TestConfig:
    """R1-UC1-S1: Verify config parsing for news fetcher parameters."""

    def test_config_keywords_and_lookback(self, fetcher_config, temp_store):
        fetcher = NewsFetcher(fetcher_config, store=temp_store)
        assert fetcher.keywords == ["有色金属"]
        assert fetcher.lookback_hours == 24
        assert fetcher.max_articles == 50

    def test_config_defaults_when_missing(self, temp_store):
        config = {"data": {"db_path": "data/test.db"}}
        fetcher = NewsFetcher(config, store=temp_store)
        assert fetcher.keywords == ["有色金属"]
        assert fetcher.lookback_hours == 24
        assert fetcher.max_articles == 50
        assert fetcher.api_delay == 0.5

    def test_config_custom_values(self, temp_store):
        config = {
            "data": {"db_path": "data/test.db", "api_delay_seconds": 1.0},
            "news": {"keywords": ["铜", "铝"], "lookback_hours": 48, "max_articles": 100},
        }
        fetcher = NewsFetcher(config, store=temp_store)
        assert fetcher.keywords == ["铜", "铝"]
        assert fetcher.lookback_hours == 48
        assert fetcher.max_articles == 100


class TestAKShareFetch:
    """R1-UC1-S2/S3, R1-UC1-E2a/E2b: AKShare API interaction tests."""

    def test_fetch_from_akshare_success(self, fetcher_config, temp_store):
        """R1-UC1-S2: Successfully fetch news from AKShare."""
        mock_df = pd.DataFrame({
            "新闻标题": ["紫金矿业发现大型铜矿", "铜价创新高"],
            "新闻内容": ["公司公告发现铜矿", "国际铜价上涨"],
            "发布时间": ["2024-01-01 10:00:00", "2024-01-01 11:00:00"],
            "文章来源": ["东方财富", "新浪财经"],
        })
        mock_ak = MagicMock()
        mock_ak.stock_news_em.return_value = mock_df
        fetcher = NewsFetcher(fetcher_config, store=temp_store)
        with patch.dict("sys.modules", {"akshare": mock_ak}):
            result = fetcher._fetch_from_akshare()
        assert len(result) == 2
        assert result[0]["title"] == "紫金矿业发现大型铜矿"

    def test_field_extraction(self, fetcher_config, temp_store):
        """R1-UC1-S3: Verify extracted fields (title, summary, published_at, source)."""
        mock_df = pd.DataFrame({
            "新闻标题": ["铜价暴涨"],
            "新闻内容": ["国际铜价创历史新高达到12000美元"],
            "发布时间": ["2024-06-15 09:30:00"],
            "文章来源": ["东方财富"],
        })
        mock_ak = MagicMock()
        mock_ak.stock_news_em.return_value = mock_df
        fetcher = NewsFetcher(fetcher_config, store=temp_store)
        with patch.dict("sys.modules", {"akshare": mock_ak}):
            result = fetcher._fetch_from_akshare()
        item = result[0]
        assert "title" in item and item["title"] == "铜价暴涨"
        assert "summary" in item
        assert "published_at" in item and item["published_at"] == "2024-06-15 09:30:00"
        assert "source" in item and item["source"] == "东方财富"
        assert "fetched_at" in item

    def test_akshare_api_failure(self, fetcher_config, temp_store):
        """R1-UC1-E2a: API failure returns empty list, logs warning."""
        mock_ak = MagicMock()
        mock_ak.stock_news_em.side_effect = Exception("Connection refused")
        fetcher = NewsFetcher(fetcher_config, store=temp_store)
        with patch.dict("sys.modules", {"akshare": mock_ak}):
            result = fetcher._fetch_from_akshare()
        assert result == []

    def test_akshare_returns_empty(self, fetcher_config, temp_store):
        """R1-UC1-E2b: API returns empty DataFrame."""
        mock_ak = MagicMock()
        mock_ak.stock_news_em.return_value = pd.DataFrame()
        fetcher = NewsFetcher(fetcher_config, store=temp_store)
        with patch.dict("sys.modules", {"akshare": mock_ak}):
            result = fetcher._fetch_from_akshare()
        assert result == []


class TestStockMatching:
    def test_match_single_stock(self, fetcher_config, temp_store):
        fetcher = NewsFetcher(fetcher_config, store=temp_store)
        news_item = {"title": "紫金矿业发现大型铜矿", "summary": "公司公告"}
        stock_names = {"601899": "紫金矿业", "600362": "江西铜业"}
        result = fetcher._match_stocks(news_item, stock_names)
        assert "601899" in result
        assert "600362" not in result

    def test_match_multiple_stocks(self, fetcher_config, temp_store):
        fetcher = NewsFetcher(fetcher_config, store=temp_store)
        news_item = {"title": "紫金矿业和江西铜业联合投资", "summary": ""}
        stock_names = {"601899": "紫金矿业", "600362": "江西铜业"}
        result = fetcher._match_stocks(news_item, stock_names)
        assert "601899" in result
        assert "600362" in result

    def test_no_match_returns_empty(self, fetcher_config, temp_store):
        fetcher = NewsFetcher(fetcher_config, store=temp_store)
        news_item = {"title": "有色金属板块全线上涨", "summary": ""}
        stock_names = {"601899": "紫金矿业"}
        result = fetcher._match_stocks(news_item, stock_names)
        assert result == []


class TestDeduplication:
    def test_new_article_passes(self, fetcher_config, temp_store):
        fetcher = NewsFetcher(fetcher_config, store=temp_store)
        items = [{"title": "Test News", "published_at": "2024-01-01 10:00:00",
                  "summary": "", "source": "test", "fetched_at": "2024-01-01T11:00:00"}]
        result = fetcher._deduplicate(items)
        assert len(result) == 1

    def test_existing_article_filtered(self, fetcher_config, temp_store):
        fetcher = NewsFetcher(fetcher_config, store=temp_store)
        # Insert first
        with temp_store._get_conn() as conn:
            conn.execute(
                "INSERT INTO news (title, summary, published_at, source, related_symbols, scope, fetched_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("Test News", "", "2024-01-01 10:00:00", "test", "[]", "sector", "2024-01-01T11:00:00"),
            )
        items = [{"title": "Test News", "published_at": "2024-01-01 10:00:00"}]
        result = fetcher._deduplicate(items)
        assert len(result) == 0


class TestPersistence:
    def test_save_and_read(self, fetcher_config, temp_store):
        fetcher = NewsFetcher(fetcher_config, store=temp_store)
        items = [
            {
                "title": "铜价上涨",
                "summary": "国际铜价创新高",
                "published_at": "2024-01-01 10:00:00",
                "source": "东方财富",
                "related_symbols": json.dumps(["601899"]),
                "scope": "stock",
                "fetched_at": "2024-01-01T11:00:00",
            }
        ]
        fetcher._save_to_db(items)
        df = temp_store.read_news()
        assert len(df) == 1
        assert df.iloc[0]["title"] == "铜价上涨"


class TestFetchAndStore:
    """R1-UC1 Full Flow: Integration test for fetch → match → dedup → store."""

    def test_fetch_and_store_full_flow(self, fetcher_config, temp_store):
        """R1-UC1: Complete news pipeline from fetch to storage."""
        mock_df = pd.DataFrame({
            "新闻标题": ["紫金矿业发现大型铜矿", "有色金属板块全线上涨"],
            "新闻内容": ["公司公告发现铜矿储量", "板块整体走强"],
            "发布时间": ["2024-01-01 10:00:00", "2024-01-01 11:00:00"],
            "文章来源": ["东方财富", "新浪财经"],
        })
        stock_names = {"601899": "紫金矿业", "600362": "江西铜业"}

        mock_ak = MagicMock()
        mock_ak.stock_news_em.return_value = mock_df
        with patch.dict("sys.modules", {"akshare": mock_ak}):
            fetcher = NewsFetcher(fetcher_config, store=temp_store)
            stored = fetcher.fetch_and_store(stock_names=stock_names)

        assert len(stored) == 2
        df = temp_store.read_news()
        assert len(df) == 2
        # First item should match 紫金矿业
        row0 = df[df["title"] == "紫金矿业发现大型铜矿"].iloc[0]
        assert "601899" in row0["related_symbols"]
        assert row0["scope"] == "stock"
        # Second item is sector-level
        row1 = df[df["title"] == "有色金属板块全线上涨"].iloc[0]
        assert row1["scope"] == "sector"
