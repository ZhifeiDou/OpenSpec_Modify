import pandas as pd
from quant_bot.factors.base import BaseFactor


class QualityFactor(BaseFactor):
    """Quality factors: ROE, gross margin."""

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        result["roe_score"] = result.get("roe", pd.Series(0, index=result.index)).fillna(0)
        result["gross_margin_score"] = result.get("gross_margin", pd.Series(0, index=result.index)).fillna(0)
        return result
