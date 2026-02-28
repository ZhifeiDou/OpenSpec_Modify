import pandas as pd
import numpy as np
from quant_bot.factors.base import BaseFactor


class ValueFactor(BaseFactor):
    """Value factors: EP ratio (1/PE), BP ratio (1/PB), dividend yield."""

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()

        pe = result.get("pe_ttm", pd.Series(dtype=float))
        result["ep_ratio"] = np.where(pe != 0, 1.0 / pe.replace(0, np.nan), 0)
        result["ep_ratio"] = result["ep_ratio"].fillna(0)

        pb = result.get("pb", pd.Series(dtype=float))
        result["bp_ratio"] = np.where(pb != 0, 1.0 / pb.replace(0, np.nan), 0)
        result["bp_ratio"] = result["bp_ratio"].fillna(0)

        result["div_yield"] = result.get("dividend_yield_ttm", pd.Series(0, index=result.index)).fillna(0)

        return result
