import os
import pytest
from quant_bot.signal.generator import SignalGenerator


@pytest.fixture
def generator(tmp_path):
    return SignalGenerator(output_dir=str(tmp_path))


def test_generate_signals(generator):
    current_holdings = {"601899": 0.5}
    target_positions = {"601899": 0.3, "600489": 0.35, "603799": 0.35}
    stock_names = {"601899": "紫金矿业", "600489": "中金黄金", "603799": "华友钴业"}
    scores = {"601899": 0.7, "600489": 0.9, "603799": 0.8}

    signals = generator.generate_signals(
        date="2024-06-01",
        current_holdings=current_holdings,
        target_positions=target_positions,
        stock_names=stock_names,
        scores=scores,
    )
    assert len(signals) == 3
    s_601899 = [s for s in signals if s["code"] == "601899"][0]
    assert s_601899["action"] in ["减仓", "卖出"]
    s_600489 = [s for s in signals if s["code"] == "600489"][0]
    assert s_600489["action"] == "买入"


def test_save_signals_to_csv(generator):
    signals = [
        {"date": "2024-06-01", "code": "601899", "name": "紫金矿业",
         "action": "买入", "target_weight": 0.5, "score": 0.8},
    ]
    generator.save_to_csv(signals, "2024-06-01")
    files = os.listdir(generator.output_dir)
    assert any("2024-06-01" in f for f in files)
