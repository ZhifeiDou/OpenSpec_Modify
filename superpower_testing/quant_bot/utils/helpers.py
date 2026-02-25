import os
import logging
import yaml
import pandas as pd

logger = logging.getLogger(__name__)


def load_config(config_path=None):
    """Load YAML configuration file."""
    if config_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(base_dir, "config", "config.yaml")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def get_trade_dates(start_date, end_date):
    """Get list of A-share trading dates between start and end."""
    import akshare as ak
    trade_cal = ak.tool_trade_date_hist_sina()
    trade_cal["trade_date"] = pd.to_datetime(trade_cal["trade_date"])
    mask = (trade_cal["trade_date"] >= start_date) & (trade_cal["trade_date"] <= end_date)
    dates = trade_cal.loc[mask, "trade_date"].dt.strftime("%Y-%m-%d").tolist()
    return dates


def setup_logging(level=logging.INFO):
    """Setup basic logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
