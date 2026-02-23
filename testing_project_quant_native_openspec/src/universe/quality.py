"""Liquidity and quality filters for stock universe."""

import pandas as pd


class QualityFilter:
    """Filter stocks by liquidity and quality criteria."""

    def __init__(self, min_listing_days: int = 120,
                 min_turnover: float = 0.005,
                 exclude_st: bool = True):
        self.min_listing_days = min_listing_days
        self.min_turnover = min_turnover
        self.exclude_st = exclude_st

    def filter(self, stocks: pd.DataFrame, price_data: dict[str, pd.DataFrame],
               current_date: str) -> pd.DataFrame:
        """Apply all quality filters."""
        filtered = stocks.copy()

        # Exclude ST stocks
        if self.exclude_st:
            filtered = filtered[~filtered["name"].str.contains("ST", case=False, na=False)]

        # Exclude newly listed stocks
        if "list_date" in filtered.columns:
            current = pd.to_datetime(current_date)
            filtered["list_date_dt"] = pd.to_datetime(filtered["list_date"], errors="coerce")
            filtered["listing_days"] = (current - filtered["list_date_dt"]).dt.days
            filtered = filtered[filtered["listing_days"] >= self.min_listing_days]
            filtered = filtered.drop(columns=["list_date_dt", "listing_days"])

        # Exclude low turnover stocks
        codes_to_keep = []
        for _, row in filtered.iterrows():
            code = row.get("code", "")
            if code in price_data and len(price_data[code]) >= 20:
                df = price_data[code].tail(20)
                avg_turnover = df["volume"].mean() / 1e8  # simplified turnover proxy
                if avg_turnover >= self.min_turnover:
                    codes_to_keep.append(code)
            else:
                codes_to_keep.append(code)  # keep if no price data available
        filtered = filtered[filtered["code"].isin(codes_to_keep)]

        return filtered
