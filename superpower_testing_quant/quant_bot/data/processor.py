import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataProcessor:
    """Clean and preprocess market data."""

    def clean_daily_data(self, df):
        """Remove suspended days and handle missing values."""
        df = df.copy()
        if "volume" in df.columns:
            df = df[df["volume"] > 0]
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].ffill().bfill()
        df = df.dropna(subset=["close"])
        df = df.reset_index(drop=True)
        logger.debug(f"Cleaned data: {len(df)} rows remaining")
        return df

    def merge_stock_data(self, daily_df, valuation_df):
        """Merge daily price data with valuation data on date."""
        daily_df = daily_df.copy()
        valuation_df = valuation_df.copy()
        daily_df["date"] = pd.to_datetime(daily_df["date"]).dt.strftime("%Y-%m-%d")
        valuation_df["date"] = pd.to_datetime(valuation_df["date"]).dt.strftime("%Y-%m-%d")
        merged = pd.merge(daily_df, valuation_df, on="date", how="left", suffixes=("", "_val"))
        merged = merged.ffill()
        logger.debug(f"Merged data: {len(merged)} rows")
        return merged
