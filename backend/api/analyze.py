"""
分析接口 v2
新增：
  - /api/sentiment  返回市场情绪
  - /api/backtest   返回历史胜率
  - /api/analyze    注入情绪因子 + 自动保存推荐快照
"""

from flask import Blueprint, request, jsonify
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.fetcher   import fetch_altcoins
from core.analyzer  import analyze_all
from core.sentiment import get_market_sentiment
from core.backtest  import record_recommendations, run_backtest_check, compute_stats
from datetime import datetime

analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.route("/analyze", methods=["POST"])
def analyze():
    try:
        body    = request.get_json() or {}
        count   = int(body.get("count",   20))
        min_cap = int(body.get("minCap", 3000))
        sort_by = body.get("sortBy", "marketCap")

        print(f"\n{'='*60}")
        print(f"开始分析: {count} 个币, 最小市值 {min_cap} 万")
        print(f"{'='*60}")

        # B. 先拉取市场情绪
        print("[B] 获取市场情绪...")
        sentiment = get_market_sentiment()
        print(f"    F&G={sentiment['fear_greed']['value']} ({sentiment['fear_greed']['label_cn']})  "
              f"BTC={sentiment['btc']['change_24h']:+.2f}%  "
              f"score_adjust={sentiment['score_adjust']:+d}")

        # A. 抓取代币数据（全量扫描 + 智能 K 线）
        tokens_data = fetch_altcoins(min_market_cap=min_cap * 10_000, count=count)
        if not tokens_data:
            return jsonify({"success": False, "error": "数据抓取失败，请检查网络连接"}), 500

        # 分析（注入情绪）
        results = analyze_all(tokens_data, sentiment=sentiment)

        # 排序
        if sort_by == "buyScore":
            results.sort(key=lambda x: x.get("buy_score", 0), reverse=True)
        elif sort_by == "weekChange":
            results.sort(key=lambda x: x.get("week_change", 0), reverse=True)
        elif sort_by == "turnover":
            results.sort(key=lambda x: x.get("turnover_rate", 0), reverse=True)
        for i, item in enumerate(results, 1):
            item["rank"] = i

        # C. 保存推荐快照（供回测使用）
        record_recommendations(results)

        stats = {
            "total":     len(results),
            "recommend": sum(1 for r in results if r.get("recommendation") == "推荐"),
            "watch":     sum(1 for r in results if r.get("recommendation") == "观望"),
            "avoid":     sum(1 for r in results if r.get("recommendation") == "不推荐"),
            "whale":     sum(1 for r in results if r.get("is_whale", False)),
        }

        return jsonify({
            "success":   True,
            "data":      results,
            "stats":     stats,
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500


@analyze_bp.route("/sentiment", methods=["GET"])
def sentiment_api():
    """返回当前市场情绪"""
    try:
        data = get_market_sentiment()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@analyze_bp.route("/backtest", methods=["GET"])
def backtest_api():
    """触发回测检查并返回胜率统计"""
    try:
        # 先更新到期记录，再返回统计
        stats = run_backtest_check()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@analyze_bp.route("/results", methods=["GET"])
def get_results():
    return jsonify({"success": True, "message": "请使用 POST /api/analyze 获取实时数据"})


@analyze_bp.route("/chart", methods=["GET"])
def generate_chart():
    return jsonify({"success": True, "message": "图表功能开发中"})
