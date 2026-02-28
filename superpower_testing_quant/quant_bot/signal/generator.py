import os
import csv
import logging

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Generate and output trading signals."""

    def __init__(self, output_dir="output/signals"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_signals(self, date, current_holdings, target_positions, stock_names, scores):
        """Compare current vs target positions to generate buy/sell signals."""
        signals = []
        all_codes = set(list(current_holdings.keys()) + list(target_positions.keys()))

        for code in all_codes:
            current_w = current_holdings.get(code, 0)
            target_w = target_positions.get(code, 0)
            name = stock_names.get(code, code)
            score = scores.get(code, 0)

            if target_w > 0 and current_w == 0:
                action = "买入"
            elif target_w == 0 and current_w > 0:
                action = "卖出"
            elif target_w > current_w:
                action = "加仓"
            elif target_w < current_w:
                action = "减仓"
            else:
                action = "持有"

            signals.append({
                "date": date,
                "code": code,
                "name": name,
                "action": action,
                "target_weight": round(target_w, 4),
                "score": round(score, 4),
            })

        for s in signals:
            logger.info(f"[{s['date']}] {s['code']} {s['name']} -> {s['action']} "
                        f"(target: {s['target_weight']:.2%}, score: {s['score']:.4f})")

        return signals

    def save_to_csv(self, signals, date):
        """Save signals to CSV file."""
        filename = os.path.join(self.output_dir, f"signals_{date}.csv")
        fieldnames = ["date", "code", "name", "action", "target_weight", "score"]
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(signals)
        logger.info(f"Signals saved to {filename}")
