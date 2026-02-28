import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class DataCache:
    """Local CSV cache for market data."""

    def __init__(self, cache_dir="data_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_path(self, key, data_type):
        return os.path.join(self.cache_dir, f"{key}_{data_type}.csv")

    def is_cached(self, key, data_type):
        return os.path.exists(self._get_path(key, data_type))

    def save(self, key, data_type, df):
        path = self._get_path(key, data_type)
        df.to_csv(path, index=False, encoding="utf-8-sig")
        logger.debug(f"Cached {key}/{data_type} -> {path}")

    def load(self, key, data_type):
        path = self._get_path(key, data_type)
        if not os.path.exists(path):
            return None
        df = pd.read_csv(path, encoding="utf-8-sig")
        logger.debug(f"Loaded cache {key}/{data_type} from {path}")
        return df
