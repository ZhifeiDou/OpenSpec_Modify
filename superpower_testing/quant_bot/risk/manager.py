import logging

logger = logging.getLogger(__name__)


class RiskManager:
    """Portfolio risk management: position limits, stop-loss, take-profit."""

    def __init__(self, config):
        risk_cfg = config.get("risk", {})
        self.max_position_pct = risk_cfg.get("max_position_pct", 0.3)
        self.stop_loss_pct = risk_cfg.get("stop_loss_pct", 0.08)
        self.take_profit_pct = risk_cfg.get("take_profit_pct", 0.20)

    def check_position_limits(self, target_positions):
        """Cap any position exceeding max_position_pct, redistribute excess equally."""
        adjusted = dict(target_positions)
        excess = 0.0
        uncapped = []

        for code, weight in adjusted.items():
            if weight > self.max_position_pct:
                excess += weight - self.max_position_pct
                adjusted[code] = self.max_position_pct
            else:
                uncapped.append(code)

        if uncapped and excess > 0:
            extra_per = excess / len(uncapped)
            for code in uncapped:
                adjusted[code] = min(adjusted[code] + extra_per, self.max_position_pct)

        logger.debug(f"Position limits applied: {adjusted}")
        return adjusted

    def check_stop_loss(self, holdings):
        """Return set of stock codes that trigger stop-loss."""
        triggered = set()
        for code, info in holdings.items():
            buy_price = info["buy_price"]
            current_price = info["current_price"]
            loss_pct = (buy_price - current_price) / buy_price
            if loss_pct >= self.stop_loss_pct:
                logger.warning(f"Stop-loss triggered for {code}: loss={loss_pct:.2%}")
                triggered.add(code)
        return triggered

    def check_take_profit(self, holdings):
        """Return set of stock codes that trigger take-profit."""
        triggered = set()
        for code, info in holdings.items():
            buy_price = info["buy_price"]
            current_price = info["current_price"]
            gain_pct = (current_price - buy_price) / buy_price
            if gain_pct >= self.take_profit_pct:
                logger.info(f"Take-profit triggered for {code}: gain={gain_pct:.2%}")
                triggered.add(code)
        return triggered
