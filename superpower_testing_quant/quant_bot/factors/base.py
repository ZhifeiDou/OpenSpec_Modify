from abc import ABC, abstractmethod
import pandas as pd


class BaseFactor(ABC):
    """Abstract base class for all factors."""

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate factor values. Returns DataFrame with factor columns added."""
        pass

    @staticmethod
    def zscore_normalize(series: pd.Series) -> pd.Series:
        """Cross-sectional z-score normalization."""
        mean = series.mean()
        std = series.std()
        if std == 0:
            return series * 0
        return (series - mean) / std
