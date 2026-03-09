"""Fundamental factors: PB percentile, gross margin change, ROE, EV/EBITDA."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.storage import DataStore
from src.factors.base import BaseFactor, register_factor


@register_factor
class PBPercentileFactor(BaseFactor):
    name = "pb_percentile_3y"
    category = "fundamental"

    def compute(self, universe, date, store, config):
        """PB percentile within 3-year history. Lower percentile = cheaper."""
        results = {}
        for symbol in universe:
            df = store.read_table(
                "financials", where="symbol = ?", params=(symbol,)
            )
            if df.empty or "pb" not in df.columns:
                results[symbol] = np.nan
                continue

            pb_values = pd.to_numeric(df["pb"], errors="coerce").dropna()
            if len(pb_values) < 4:
                results[symbol] = np.nan
                continue

            current_pb = pb_values.iloc[-1]
            # Percentile: fraction of historical values below current
            percentile = (pb_values < current_pb).mean()
            results[symbol] = percentile

        return pd.Series(results)


@register_factor
class GrossMarginChangeFactor(BaseFactor):
    name = "gross_margin_qoq"
    category = "fundamental"

    def compute(self, universe, date, store, config):
        """Gross margin quarter-over-quarter change."""
        results = {}
        for symbol in universe:
            df = store.read_table(
                "financials", where="symbol = ?", params=(symbol,)
            )
            if df.empty or "gross_margin" not in df.columns or len(df) < 2:
                results[symbol] = np.nan
                continue

            gm = pd.to_numeric(df["gross_margin"], errors="coerce").dropna()
            if len(gm) < 2:
                results[symbol] = np.nan
                continue

            results[symbol] = gm.iloc[-1] - gm.iloc[-2]

        return pd.Series(results)


@register_factor
class ROETTMFactor(BaseFactor):
    name = "roe_ttm"
    category = "fundamental"

    def compute(self, universe, date, store, config):
        """Return on equity (trailing twelve months)."""
        results = {}
        for symbol in universe:
            df = store.read_table(
                "financials", where="symbol = ?", params=(symbol,)
            )
            if df.empty or "roe_ttm" not in df.columns:
                results[symbol] = np.nan
                continue

            roe = pd.to_numeric(df["roe_ttm"], errors="coerce").dropna()
            results[symbol] = roe.iloc[-1] if len(roe) > 0 else np.nan

        return pd.Series(results)


@register_factor
class EVEBITDAFactor(BaseFactor):
    name = "ev_ebitda"
    category = "fundamental"

    def compute(self, universe, date, store, config):
        """Enterprise value to EBITDA ratio. Lower = cheaper."""
        results = {}
        for symbol in universe:
            df = store.read_table(
                "financials", where="symbol = ?", params=(symbol,)
            )
            if df.empty:
                results[symbol] = np.nan
                continue

            ev = pd.to_numeric(df.get("ev", pd.Series()), errors="coerce").dropna()
            ebitda = pd.to_numeric(df.get("ebitda", pd.Series()), errors="coerce").dropna()

            if len(ev) == 0 or len(ebitda) == 0 or ebitda.iloc[-1] == 0:
                results[symbol] = np.nan
            else:
                results[symbol] = ev.iloc[-1] / ebitda.iloc[-1]

        return pd.Series(results)
