"""Factor base class and registry — decorator-based factor registration."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

from src.data.storage import DataStore
from src.factors.standardizer import cross_sectional_standardize

logger = logging.getLogger(__name__)

# Global factor registry
_FACTOR_REGISTRY: dict[str, type["BaseFactor"]] = {}


def register_factor(cls: type["BaseFactor"]) -> type["BaseFactor"]:
    """Decorator to register a factor class."""
    _FACTOR_REGISTRY[cls.name] = cls
    return cls


def get_registered_factors() -> dict[str, type["BaseFactor"]]:
    return dict(_FACTOR_REGISTRY)


class BaseFactor(ABC):
    """Base class for all factors."""

    name: str = ""
    category: str = ""  # fundamental, technical, commodity, macro, flow

    @abstractmethod
    def compute(
        self, universe: list[str], date: str, store: DataStore, config: dict
    ) -> pd.Series:
        """Compute factor values for all stocks in the universe.

        Returns a pd.Series indexed by symbol with factor values.
        NaN for stocks where the factor cannot be computed.
        """
        ...


def compute_all_factors(
    config: dict, date: str | None = None, store: DataStore | None = None
) -> pd.DataFrame:
    """Compute all registered factors for the current universe.

    Returns a DataFrame: rows=stocks, columns=factor names.
    All values are cross-sectionally standardized (MAD + Z-Score).
    """
    # Lazy imports to trigger factor registration
    import src.factors.fundamental  # noqa: F401
    import src.factors.technical  # noqa: F401
    import src.factors.commodity  # noqa: F401
    import src.factors.macro  # noqa: F401
    import src.factors.flow  # noqa: F401

    from src.universe.classifier import get_universe

    if store is None:
        data_cfg = config.get("data", {})
        store = DataStore(data_cfg.get("db_path", "data/quant.db"))

    if date is None:
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")

    # Get universe
    universe_df = get_universe(config, date=date, store=store)
    if universe_df.empty:
        logger.warning("Empty universe, cannot compute factors")
        return pd.DataFrame()

    symbols = universe_df["symbol"].tolist()

    # Cache universe so commodity factors can look up sub-sectors
    try:
        store.save_dataframe("universe_cache", universe_df)
    except Exception:
        # Table may not exist; create it first
        with store._get_conn() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS universe_cache "
                "(symbol TEXT PRIMARY KEY, name TEXT, subsector TEXT)"
            )
        store.save_dataframe("universe_cache", universe_df)

    factor_cfg = config.get("factors", {})
    small_warning = factor_cfg.get("small_universe_warning", 10)
    if len(symbols) < small_warning:
        logger.warning(
            "Universe has only %d stocks (< %d), cross-sectional standardization may be unreliable",
            len(symbols), small_warning,
        )

    # Compute each factor
    results = {}
    for name, factor_cls in _FACTOR_REGISTRY.items():
        try:
            factor = factor_cls()
            values = factor.compute(symbols, date, store, config)
            results[name] = values
        except Exception as e:
            logger.error("Failed to compute factor %s: %s", name, e)
            results[name] = pd.Series(np.nan, index=symbols)

    factor_matrix = pd.DataFrame(results, index=symbols)

    # Cross-sectional standardization
    mad_multiple = factor_cfg.get("winsorize_mad_multiple", 3.0)
    factor_matrix = cross_sectional_standardize(factor_matrix, mad_multiple)

    return factor_matrix
