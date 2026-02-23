"""Flask主应用 — Web路由 + API"""

import json
import traceback
from flask import Flask, render_template, jsonify, request

from config import FACTOR_WEIGHTS, BACKTEST, STRATEGY
from data_fetcher import get_nonferrous_stocks, get_stock_history
from factor_engine import compute_all_factors
from strategy import generate_signals, select_portfolio
from backtester import run_backtest

app = Flask(__name__)

# ── 全局缓存（进程内） ──
_cache = {
    "stock_list": None,
    "scores_df": None,
    "signals": None,
    "backtest_result": None,
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/universe")
def api_universe():
    """股票池列表"""
    try:
        if _cache["stock_list"] is None:
            df = get_nonferrous_stocks()
            _cache["stock_list"] = df.to_dict("records")
        return jsonify({"ok": True, "data": _cache["stock_list"]})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/factors")
def api_factors():
    """当前因子评分"""
    try:
        if _cache["scores_df"] is None:
            return jsonify({"ok": False, "error": "请先刷新数据"})
        df = _cache["scores_df"]
        # 选取要返回的列
        cols = ["code", "name", "composite_score", "rank",
                "ret_5d", "ret_20d", "macd", "rsi", "pe_percentile",
                "pb_percentile", "roe", "main_net_inflow"]
        available = [c for c in cols if c in df.columns]
        data = df[available].round(4).to_dict("records")
        return jsonify({"ok": True, "data": data})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/signals")
def api_signals():
    """最新交易信号"""
    try:
        if _cache["signals"] is None:
            return jsonify({"ok": False, "error": "请先刷新数据"})
        return jsonify({"ok": True, "data": _cache["signals"]})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/backtest")
def api_backtest():
    """回测结果"""
    try:
        if _cache["backtest_result"] is None:
            return jsonify({"ok": False, "error": "请先运行回测"})
        return jsonify({"ok": True, "data": _cache["backtest_result"]})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/kline/<code>")
def api_kline(code):
    """获取个股K线数据"""
    try:
        start = request.args.get("start", BACKTEST["start_date"])
        end = request.args.get("end", BACKTEST["end_date"])
        df = get_stock_history(code, start=start, end=end)
        if df is None or df.empty:
            return jsonify({"ok": False, "error": "无数据"})
        data = df[["date", "open", "high", "low", "close", "volume"]].to_dict("records")
        return jsonify({"ok": True, "data": data})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """刷新数据 → 重新计算因子和信号"""
    try:
        # 获取前端传来的权重（可选）
        body = request.get_json(silent=True) or {}
        custom_weights = body.get("weights", None)
        weights = custom_weights if custom_weights else FACTOR_WEIGHTS

        # 1. 获取股票池
        df = get_nonferrous_stocks(force=True)
        stock_list = df.to_dict("records")
        _cache["stock_list"] = stock_list

        # 2. 计算因子评分
        scores = compute_all_factors(stock_list, weights=weights)
        _cache["scores_df"] = scores

        # 3. 生成信号
        signals = generate_signals(scores)
        _cache["signals"] = signals

        return jsonify({
            "ok": True,
            "message": f"已刷新 {len(stock_list)} 只股票的数据和因子评分",
            "stock_count": len(stock_list),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/run_backtest", methods=["POST"])
def api_run_backtest():
    """运行回测"""
    try:
        if _cache["stock_list"] is None:
            return jsonify({"ok": False, "error": "请先刷新数据"})

        result = run_backtest(_cache["stock_list"])
        result["metrics"]["total_trades"] = len(result["trades"])
        _cache["backtest_result"] = result

        return jsonify({"ok": True, "data": result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


if __name__ == "__main__":
    print("=" * 50)
    print("  Nonferrous Metal Quant Robot")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
