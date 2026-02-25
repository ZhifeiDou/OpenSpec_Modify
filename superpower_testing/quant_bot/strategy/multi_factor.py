import logging
import numpy as np
from quant_bot.factors.base import BaseFactor

logger = logging.getLogger(__name__)


class MultiFactorStrategy:
    """Multi-factor stock selection strategy with cross-sectional scoring."""

    FACTOR_COLUMNS = {
        "momentum": ([("return_n", 1), ("rsi", -1), ("price_position", 1)]),
        "value": ([("ep_ratio", 1), ("bp_ratio", 1), ("div_yield", 1)]),
        "volatility": ([("hist_volatility", -1), ("atr", -1)]),
        "quality": ([("roe_score", 1), ("gross_margin_score", 1)]),
    }

    def __init__(self, config):
        self.factor_weights = {k: v.get("weight", 0.25) for k, v in config["factors"].items()}
        self.top_n = config["strategy"]["top_n"]

    def score_stocks(self, stocks_data):
        """Score stocks cross-sectionally using multi-factor model.

        Args:
            stocks_data: dict of {stock_code: {factor_col: value, ...}}

        Returns:
            dict of {stock_code: composite_score}
        """
        codes = list(stocks_data.keys())
        if not codes:
            return {}

        composite_scores = {code: 0.0 for code in codes}

        for group_name, factor_cols in self.FACTOR_COLUMNS.items():
            group_weight = self.factor_weights.get(group_name, 0)
            if group_weight == 0:
                continue

            for col_name, direction in factor_cols:
                values = []
                for code in codes:
                    val = stocks_data[code].get(col_name)
                    values.append(val if val is not None else np.nan)

                values = np.array(values, dtype=float)
                valid_mask = ~np.isnan(values)

                if valid_mask.sum() < 2:
                    continue

                mean = np.nanmean(values)
                std = np.nanstd(values)
                if std == 0:
                    continue
                z_scores = (values - mean) / std * direction

                col_weight = group_weight / len(factor_cols)
                for i, code in enumerate(codes):
                    if valid_mask[i]:
                        composite_scores[code] += z_scores[i] * col_weight

        return composite_scores

    def select_top_n(self, scores):
        """Select top N stocks by composite score."""
        sorted_stocks = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        selected = [code for code, _ in sorted_stocks[:self.top_n]]
        logger.info(f"Selected top {self.top_n}: {selected}")
        return selected

    def generate_target_positions(self, selected_stocks):
        """Generate equal-weight target positions."""
        if not selected_stocks:
            return {}
        weight = 1.0 / len(selected_stocks)
        return {code: weight for code in selected_stocks}
