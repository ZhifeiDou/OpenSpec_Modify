"""CSRC industry code filtering for non-ferrous metals."""

import pandas as pd
from src.data.fetcher import DataFetcher


class UniverseFilter:
    """Filter stocks by CSRC non-ferrous metals industry classification."""

    def __init__(self, industry_code: str = "C22"):
        self.industry_code = industry_code

    def filter_by_industry(self, fetcher: DataFetcher) -> pd.DataFrame:
        """Get all stocks in the non-ferrous metals industry."""
        for name, api in fetcher.apis:
            if name == "akshare":
                try:
                    classification = api.fetch_industry_classification()
                    metals = classification[
                        classification["行业代码"].str.startswith(self.industry_code)
                    ]
                    return metals
                except Exception:
                    continue
        return pd.DataFrame()
