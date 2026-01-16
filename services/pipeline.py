"""
Pipeline orchestration for market risk detection.
- Loads seed news
- Runs sentiment analysis
- Marks alerts
- Produces dashboard metrics and reports
"""

from __future__ import annotations

import glob
import json
import os
from datetime import datetime
from typing import Dict, List

from .sentiment import sentiment_analyzer
from .brief import brief_generator

# Seed news (fallback when no crawler data is available)
SEED_NEWS = [
    {
        "id": 1,
        "title": "某科技公司业绩预警，预计季度亏损超5亿元",
        "content": "公告称受需求下滑和成本上升影响，主要产品线销售大幅下降，或有减值风险。",
        "source": "东方财富",
        "publish_time": "2026-01-15 09:30:00",
        "stock_code": "300001.SZ",
        "stock_name": "示例科技",
        "stock_industry": "科技",
    },
    {
        "id": 2,
        "title": "监管机构对某银行开展专项检查，涉及违规放贷问题",
        "content": "本次检查重点针对房地产相关贷款业务，市场担忧或触发罚款与拨备压力。",
        "source": "东方财富",
        "publish_time": "2026-01-15 10:15:00",
        "stock_code": "601398.SH",
        "stock_name": "示例银行",
        "stock_industry": "金融",
    },
    {
        "id": 3,
        "title": "龙头白酒销量恢复，渠道库存回归正常区间",
        "content": "节后动销表现优于预期，经销商反馈补货节奏平稳，行业景气度边际改善。",
        "source": "东方财富",
        "publish_time": "2026-01-15 11:00:00",
        "stock_code": "600519.SH",
        "stock_name": "贵州茅台",
        "stock_industry": "消费",
    },
    {
        "id": 4,
        "title": "新能源车企发布销量快报，单月交付创新高",
        "content": "公司推出新款车型并加大促销力度，单月交付同比增长超80%，盈利能力有望提升。",
        "source": "东方财富",
        "publish_time": "2026-01-15 11:30:00",
        "stock_code": "300750.SZ",
        "stock_name": "宁德时代",
        "stock_industry": "新能源",
    },
    {
        "id": 5,
        "title": "地产企业爆出债务违约，或触发交叉违约条款",
        "content": "资金链紧张导致美元债未能按期兑付，市场担忧后续项目停工与资产处置风险。",
        "source": "东方财富",
        "publish_time": "2026-01-15 13:00:00",
        "stock_code": "000002.SZ",
        "stock_name": "万科A",
        "stock_industry": "房地产",
    },
    {
        "id": 6,
        "title": "芯片厂商获大订单，管理层上调全年指引",
        "content": "海外大客户新增采购，订单能见度提升；公司计划扩大产能，资本开支略有上调。",
        "source": "东方财富",
        "publish_time": "2026-01-15 14:20:00",
        "stock_code": "688981.SH",
        "stock_name": "中芯国际",
        "stock_industry": "半导体",
    },
    {
        "id": 7,
        "title": "化工园区发生安全事故，相关企业停产自查",
        "content": "初步调查显示存在安全管理缺陷，监管部门已进驻，市场担忧产能恢复时间。",
        "source": "东方财富",
        "publish_time": "2026-01-15 15:10:00",
        "stock_code": "600309.SH",
        "stock_name": "万华化学",
        "stock_industry": "化工",
    },
    {
        "id": 8,
        "title": "某券商发布策略：短期市场情绪回暖，关注高股息板块",
        "content": "宏观流动性保持宽松，资金偏好防御与高分红标的，建议均衡配置。",
        "source": "东方财富",
        "publish_time": "2026-01-15 16:00:00",
        "stock_code": "600030.SH",
        "stock_name": "中信证券",
        "stock_industry": "金融",
    },
]
def load_news() -> List[Dict]:
    """Load news from crawler JSON if available; fallback to seeds."""
    data = _load_from_json()
    if data:
        return data
    return [item.copy() for item in SEED_NEWS]


def analyze_news(news_items: List[Dict]) -> List[Dict]:
    analyzed = []
    for item in news_items:
        sentiment = sentiment_analyzer.analyze(item.get("content", ""), item.get("title", ""))
        enriched = {**item, **sentiment}
        enriched["is_risk"] = enriched.get("sentiment_label") == "风险"
        enriched["alert"] = enriched["is_risk"] and enriched.get("confidence", 0) >= 0.6
        enriched["score_bucket"] = _bucket_score(enriched.get("sentiment_score", 0))
        analyzed.append(enriched)
    return analyzed


def compute_dashboard(processed_news: List[Dict]) -> Dict:
    total = len(processed_news)
    risk_news = [n for n in processed_news if n.get("is_risk")]
    risk_count = len(risk_news)
    avg_confidence = round(sum(n.get("confidence", 0) for n in risk_news) / risk_count, 3) if risk_count else 0
    alert_count = sum(1 for n in processed_news if n.get("alert"))
    high_risk = sum(1 for n in processed_news if n.get("sentiment_score", 0) < -0.5)
    medium_risk = sum(1 for n in processed_news if -0.5 <= n.get("sentiment_score", 0) < -0.2)
    keyword_total = sum(n.get("keyword_counts", {}).get("risk", 0) for n in processed_news)
    return {
        "total_news": total,
        "risk_news_count": risk_count,
        "risk_ratio": round((risk_count / total) * 100, 1) if total else 0,
        "avg_confidence": avg_confidence,
        "alert_count": alert_count,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "keyword_hits": int(keyword_total),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def generate_alerts(processed_news: List[Dict]) -> List[Dict]:
    return [
        {
            "id": n["id"],
            "title": n["title"],
            "stock_code": n.get("stock_code"),
            "confidence": n.get("confidence"),
            "sentiment_score": n.get("sentiment_score"),
            "publish_time": n.get("publish_time"),
        }
        for n in processed_news
        if n.get("alert")
    ]


def run_pipeline() -> Dict:
    news = load_news()
    processed = analyze_news(news)
    alerts = generate_alerts(processed)
    dashboard = compute_dashboard(processed)
    risk_articles = [n["title"] for n in processed if n.get("is_risk")]
    brief = brief_generator.generate_risk_briefing("000000", "市场组合", risk_articles)
    market_report = brief_generator.generate_market_report(processed)
    return {
        "news": processed,
        "alerts": alerts,
        "dashboard": dashboard,
        "risk_brief": brief,
        "market_report": market_report,
    }


def _bucket_score(score: float) -> str:
    if score < -0.5:
        return "高风险"
    if score < -0.2:
        return "中风险"
    if score < 0.3:
        return "中性"
    return "正面"


def _load_from_json() -> List[Dict]:
    """Read latest crawler JSON; return sanitized list or empty."""
    path = _find_latest_json()
    if not path:
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        if not isinstance(payload, list):
            return []
        items = []
        for idx, item in enumerate(payload, 1):
            normalized = _normalize_article(item, idx)
            items.append(normalized)
        return items
    except Exception:
        return []


def _find_latest_json() -> str | None:
    """Pick latest JSON from env path or known folders."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    patterns = [
        os.getenv("CRAWLER_JSON_PATH"),
        os.path.join(base_dir, "data", "*.json"),
        os.path.join(base_dir, "..", "market-risk-analysis", "src", "crawler", "articles_*.json"),
    ]
    candidates: List[str] = []
    for pattern in patterns:
        if not pattern:
            continue
        if os.path.isfile(pattern):
            candidates.append(pattern)
        else:
            candidates.extend(glob.glob(pattern))
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def _normalize_article(item: Dict, idx: int) -> Dict:
    """Ensure required fields exist for downstream processing."""
    title = item.get("title") or item.get("content") or "未命名新闻"
    content = item.get("content") or title
    publish_time = item.get("publish_time") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stock_code = item.get("stock_code") or "000000"
    return {
        "id": item.get("id", idx),
        "title": title,
        "content": content,
        "source": item.get("source", "东方财富"),
        "publish_time": publish_time,
        "stock_code": stock_code,
        "stock_name": item.get("stock_name", stock_code),
        "stock_industry": item.get("stock_industry", "未知"),
    }


def get_data_source_info() -> Dict:
    """Return info about which JSON is used and counts."""
    path = _find_latest_json()
    info: Dict = {
        "json_path": path or "",
        "used_seed": False,
        "news_count": 0,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    data = _load_from_json()
    if data:
        info["news_count"] = len(data)
        return info
    info["used_seed"] = True
    info["news_count"] = len(SEED_NEWS)
    return info
