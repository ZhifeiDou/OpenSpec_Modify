"""Multi-source data fetching with auto-failover."""

import logging
import pandas as pd
import yaml

from src.data.api_akshare import AKShareAPI
from src.data.api_baostock import BaoStockAPI
from src.data.api_tushare import TushareAPI
from src.data.cache import DataCache

logger = logging.getLogger(__name__)


class DataSourceError(Exception):
    """Raised when all data sources fail."""
    pass


class DataFetcher:
    """Multi-source data fetcher with auto-failover and caching."""

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        data_config = config["data"]
        sources = sorted(data_config["sources"], key=lambda s: s["priority"])

        self.apis = []
        for src in sources:
            name = src["name"]
            delay = src.get("delay_seconds", 0.5)
            if name == "akshare":
                self.apis.append(("akshare", AKShareAPI(delay=delay)))
            elif name == "baostock":
                self.apis.append(("baostock", BaoStockAPI(delay=delay)))
            elif name == "tushare":
                token = src.get("token", "")
                self.apis.append(("tushare", TushareAPI(token=token, delay=delay)))

        cache_config = data_config.get("cache", {})
        self.cache = DataCache(db_path=cache_config.get("db_path", "data/cache.db"))

    def fetch_stock_price(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch stock prices with cache-first, then failover through sources."""
        if self.cache.has_data("stock_prices", "code", code, start_date, end_date):
            logger.info(f"Cache hit for {code} [{start_date}, {end_date}]")
            return self.cache.get_stock_prices(code, start_date, end_date)

        latest = self.cache.get_latest_date("stock_prices", "code", code)
        fetch_start = latest if latest and latest > start_date else start_date

        errors = []
        for name, api in self.apis:
            try:
                logger.info(f"Fetching {code} from {name}")
                df = api.fetch_stock_price(code, fetch_start, end_date)
                if len(df) > 0:
                    self.cache.save_stock_prices(code, df)
                return self.cache.get_stock_prices(code, start_date, end_date)
            except Exception as e:
                logger.warning(f"{name} failed for {code}: {e}")
                errors.append(f"{name}: {e}")

        raise DataSourceError(f"All sources failed for stock {code}: {'; '.join(errors)}")

    def fetch_fundamental(self, code: str) -> dict:
        """Fetch fundamental data with failover."""
        errors = []
        for name, api in self.apis:
            try:
                result = api.fetch_fundamental(code)
                if any(v is not None for v in result.values()):
                    return result
            except Exception as e:
                logger.warning(f"{name} fundamental failed for {code}: {e}")
                errors.append(f"{name}: {e}")
        raise DataSourceError(f"All sources failed for fundamentals {code}: {'; '.join(errors)}")

    def fetch_metal_futures(self, metal: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch metal futures prices with cache."""
        if self.cache.has_data("metal_futures", "metal", metal, start_date, end_date):
            return self.cache.get_metal_futures(metal, start_date, end_date)

        for name, api in self.apis:
            if name == "akshare":
                try:
                    df = api.fetch_metal_futures(metal, start_date, end_date)
                    if len(df) > 0:
                        self.cache.save_metal_futures(metal, df)
                    return self.cache.get_metal_futures(metal, start_date, end_date)
                except Exception as e:
                    logger.warning(f"Metal futures fetch failed: {e}")
        return pd.DataFrame(columns=["date", "close"])

    def fetch_macro_pmi(self) -> pd.DataFrame:
        """Fetch PMI data."""
        for name, api in self.apis:
            if name == "akshare":
                try:
                    return api.fetch_macro_pmi()
                except Exception as e:
                    logger.warning(f"PMI fetch failed: {e}")
        return pd.DataFrame(columns=["date", "pmi"])

    def fetch_northbound_flow(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch northbound fund flow."""
        for name, api in self.apis:
            if name == "akshare":
                try:
                    return api.fetch_northbound_flow(start_date, end_date)
                except Exception as e:
                    logger.warning(f"Northbound flow fetch failed: {e}")
        return pd.DataFrame(columns=["date", "net_flow"])

    def close(self):
        self.cache.close()
        for name, api in self.apis:
            if hasattr(api, "logout"):
                api.logout()
