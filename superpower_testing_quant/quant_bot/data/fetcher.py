import logging
import time
import akshare as ak
import pandas as pd

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def _retry(func, *args, **kwargs):
    """Retry a function call with exponential backoff."""
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_DELAY * (attempt + 1)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise


class DataFetcher:
    """Fetch A-share data from AKShare."""

    def get_sector_stocks(self, sector_name="有色金属"):
        """Get stock list for a sector (板块成分股)."""
        try:
            df = _retry(ak.stock_board_industry_cons_em, symbol=sector_name)
            result = df[["代码", "名称"]].copy()
            result.columns = ["code", "name"]
            logger.info(f"Fetched {len(result)} stocks for sector: {sector_name}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch sector stocks: {e}")
            raise

    def get_stock_daily(self, stock_code, start_date, end_date):
        """Get daily kline data for a stock."""
        try:
            df = _retry(
                ak.stock_zh_a_hist,
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq",
            )
            df = df.rename(columns={
                "日期": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
                "振幅": "amplitude",
                "涨跌幅": "pct_change",
                "涨跌额": "change",
                "换手率": "turnover",
            })
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            logger.info(f"Fetched {len(df)} daily bars for {stock_code}")
            return df
        except Exception as e:
            logger.error(f"Failed to fetch daily data for {stock_code}: {e}")
            raise

    def get_stock_valuation(self, stock_code):
        """Get valuation indicators (PE, PB, etc.) for a stock."""
        try:
            df = _retry(ak.stock_a_indicator_lg, symbol=stock_code)
            df = df.rename(columns={
                "trade_date": "date",
                "pe": "pe",
                "pe_ttm": "pe_ttm",
                "pb": "pb",
                "ps": "ps",
                "ps_ttm": "ps_ttm",
                "dv_ratio": "dividend_yield",
                "dv_ttm": "dividend_yield_ttm",
                "total_mv": "total_mv",
            })
            logger.info(f"Fetched valuation data for {stock_code}")
            return df
        except Exception as e:
            logger.error(f"Failed to fetch valuation for {stock_code}: {e}")
            raise
