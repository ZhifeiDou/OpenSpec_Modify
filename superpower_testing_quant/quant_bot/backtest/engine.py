import logging
import numpy as np
import pandas as pd
from quant_bot.factors.momentum import MomentumFactor
from quant_bot.factors.value import ValueFactor
from quant_bot.factors.volatility import VolatilityFactor
from quant_bot.factors.quality import QualityFactor
from quant_bot.strategy.multi_factor import MultiFactorStrategy
from quant_bot.risk.manager import RiskManager

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Backtesting engine: iterate over trading days, simulate portfolio."""

    def __init__(self, config):
        self.config = config
        self.initial_capital = config["backtest"]["initial_capital"]
        self.commission = config["backtest"]["commission"]
        self.slippage = config["backtest"]["slippage"]
        self.strategy = MultiFactorStrategy(config)
        self.risk_manager = RiskManager(config)

        lookback_m = config["factors"].get("momentum", {}).get("lookback", 20)
        lookback_v = config["factors"].get("volatility", {}).get("lookback", 20)
        self.factors = {
            "momentum": MomentumFactor(lookback=lookback_m),
            "value": ValueFactor(),
            "volatility": VolatilityFactor(lookback=lookback_v),
            "quality": QualityFactor(),
        }

    def _compute_factors_for_stock(self, df):
        """Apply all factors to a stock's DataFrame."""
        result = df.copy()
        for factor in self.factors.values():
            result = factor.calculate(result)
        return result

    def run(self, stocks_data, stock_names):
        """Run backtest.

        Args:
            stocks_data: dict of {stock_code: DataFrame with date,open,close,high,low,volume,...}
            stock_names: dict of {stock_code: stock_name}

        Returns:
            dict with portfolio_values, trades, metrics
        """
        # Compute factors for all stocks
        factor_data = {}
        for code, df in stocks_data.items():
            factor_data[code] = self._compute_factors_for_stock(df)

        # Get common trading dates
        all_dates = set()
        for df in factor_data.values():
            all_dates.update(df["date"].tolist())
        dates = sorted(all_dates)

        # Portfolio state
        cash = self.initial_capital
        holdings = {}  # {code: {"shares": int, "buy_price": float}}
        portfolio_values = []
        trades = []
        daily_returns = []

        for i, date in enumerate(dates):
            # Get current prices
            current_prices = {}
            for code, df in factor_data.items():
                row = df[df["date"] == date]
                if not row.empty:
                    current_prices[code] = row["close"].values[0]

            # Calculate portfolio value
            holdings_value = sum(
                holdings[c]["shares"] * current_prices.get(c, 0)
                for c in holdings if c in current_prices
            )
            total_value = cash + holdings_value
            portfolio_values.append({"date": date, "value": total_value})

            if len(portfolio_values) > 1:
                prev_val = portfolio_values[-2]["value"]
                daily_ret = (total_value - prev_val) / prev_val if prev_val > 0 else 0
                daily_returns.append(daily_ret)

            # Risk checks: stop-loss / take-profit
            if holdings:
                risk_holdings = {
                    c: {"buy_price": h["buy_price"], "current_price": current_prices.get(c, h["buy_price"])}
                    for c, h in holdings.items() if c in current_prices
                }
                stop_loss_codes = self.risk_manager.check_stop_loss(risk_holdings)
                take_profit_codes = self.risk_manager.check_take_profit(risk_holdings)
                force_sell = stop_loss_codes | take_profit_codes

                for code in force_sell:
                    if code in holdings and code in current_prices:
                        sell_price = current_prices[code] * (1 - self.slippage)
                        proceeds = holdings[code]["shares"] * sell_price
                        proceeds -= proceeds * self.commission
                        cash += proceeds
                        trades.append({"date": date, "code": code, "action": "止损/止盈卖出",
                                       "price": sell_price, "shares": holdings[code]["shares"]})
                        del holdings[code]

            # Strategy: score and select stocks
            stocks_factor_snapshot = {}
            for code, df in factor_data.items():
                row = df[df["date"] == date]
                if row.empty:
                    continue
                row_dict = row.iloc[0].to_dict()
                if pd.notna(row_dict.get("return_n")):
                    stocks_factor_snapshot[code] = row_dict

            if len(stocks_factor_snapshot) < 2:
                continue

            scores = self.strategy.score_stocks(stocks_factor_snapshot)
            selected = self.strategy.select_top_n(scores)
            target_positions = self.strategy.generate_target_positions(selected)
            target_positions = self.risk_manager.check_position_limits(target_positions)

            # Rebalance: sell positions not in target
            for code in list(holdings.keys()):
                if code not in target_positions and code in current_prices:
                    sell_price = current_prices[code] * (1 - self.slippage)
                    proceeds = holdings[code]["shares"] * sell_price
                    proceeds -= proceeds * self.commission
                    cash += proceeds
                    trades.append({"date": date, "code": code, "action": "卖出",
                                   "price": sell_price, "shares": holdings[code]["shares"]})
                    del holdings[code]

            # Buy target positions
            for code, weight in target_positions.items():
                if code not in current_prices:
                    continue
                target_value = total_value * weight
                current_value = holdings.get(code, {}).get("shares", 0) * current_prices[code]
                diff = target_value - current_value

                if diff > current_prices[code]:  # Buy
                    buy_price = current_prices[code] * (1 + self.slippage)
                    shares_to_buy = int(diff / buy_price / 100) * 100  # Round to 100 shares (A-share lot size)
                    if shares_to_buy > 0:
                        cost = shares_to_buy * buy_price * (1 + self.commission)
                        if cost <= cash:
                            cash -= cost
                            existing_shares = holdings.get(code, {}).get("shares", 0)
                            holdings[code] = {
                                "shares": existing_shares + shares_to_buy,
                                "buy_price": buy_price,
                            }
                            trades.append({"date": date, "code": code, "action": "买入",
                                           "price": buy_price, "shares": shares_to_buy})

        # Calculate metrics
        metrics = self._calculate_metrics(portfolio_values, daily_returns)

        return {
            "portfolio_values": portfolio_values,
            "trades": trades,
            "metrics": metrics,
        }

    def _calculate_metrics(self, portfolio_values, daily_returns):
        """Calculate backtest performance metrics."""
        if len(portfolio_values) < 2:
            return {"annual_return": 0, "max_drawdown": 0, "sharpe_ratio": 0, "win_rate": 0, "total_return": 0, "total_trades": 0}

        values = [pv["value"] for pv in portfolio_values]
        total_return = (values[-1] - values[0]) / values[0]
        n_days = len(values)
        annual_return = (1 + total_return) ** (252 / max(n_days, 1)) - 1

        # Max drawdown
        peak = values[0]
        max_dd = 0
        for v in values:
            peak = max(peak, v)
            dd = (peak - v) / peak
            max_dd = max(max_dd, dd)

        # Sharpe ratio (annualized)
        if daily_returns:
            avg_ret = np.mean(daily_returns)
            std_ret = np.std(daily_returns)
            sharpe = (avg_ret / std_ret * np.sqrt(252)) if std_ret > 0 else 0
        else:
            sharpe = 0

        # Win rate (% of positive daily returns)
        if daily_returns:
            win_rate = sum(1 for r in daily_returns if r > 0) / len(daily_returns)
        else:
            win_rate = 0

        metrics = {
            "total_return": round(total_return, 4),
            "annual_return": round(annual_return, 4),
            "max_drawdown": round(max_dd, 4),
            "sharpe_ratio": round(sharpe, 4),
            "win_rate": round(win_rate, 4),
            "total_trades": len(daily_returns),
        }
        logger.info(f"Backtest metrics: {metrics}")
        return metrics
