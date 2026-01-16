"""
Brief generation service
Uses mock LLM logic to produce concise risk briefings and market reports.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class BriefGenerator:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.model_name = "mock" if use_mock else "gpt-3.5-turbo"
        self.status = {
            "use_mock": use_mock,
            "model_name": self.model_name,
            "generated_count": 0,
            "last_generated": None,
        }

    def generate_risk_briefing(
        self,
        stock_code: str,
        stock_name: str,
        risk_articles: List[str],
        additional_context: str = "",
    ) -> str:
        try:
            briefing = self._generate_mock_briefing(stock_code, stock_name, risk_articles)
            self.status["generated_count"] += 1
            self.status["last_generated"] = datetime.now().isoformat()
            return briefing
        except Exception as exc:  # pragma: no cover
            logger.error("生成风险简报失败: %s", exc)
            return self._generate_error_briefing(stock_code, stock_name, str(exc))

    def generate_market_report(self, risk_data: List[Dict], market_context: str = "") -> str:
        summary = self._summarize_risk_data(risk_data)
        return self._generate_mock_market_report(summary, market_context)

    def _summarize_risk_data(self, risk_data: List[Dict]) -> Dict:
        if not risk_data:
            return {"total": 0, "high_risk": 0, "medium_risk": 0, "low_risk": 0, "stocks": [], "industries": []}
        summary = {"total": len(risk_data), "high_risk": 0, "medium_risk": 0, "low_risk": 0, "stocks": set(), "industries": set()}
        for item in risk_data:
            score = item.get("sentiment_score", 0)
            if score < -0.5:
                summary["high_risk"] += 1
            elif score < -0.2:
                summary["medium_risk"] += 1
            else:
                summary["low_risk"] += 1
            if item.get("stock_code"):
                summary["stocks"].add(item["stock_code"])
            if item.get("stock_industry"):
                summary["industries"].add(item["stock_industry"])
        summary["stocks"] = list(summary["stocks"])
        summary["industries"] = list(summary["industries"])
        return summary

    def _generate_mock_briefing(self, stock_code: str, stock_name: str, risk_articles: List[str]) -> str:
        now = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        count = len(risk_articles)
        if count >= 5:
            risk_level = "高"
            impact = "显著"
        elif count >= 3:
            risk_level = "中"
            impact = "中等"
        else:
            risk_level = "低"
            impact = "有限"
        return (
            f"《市场风险应对简报》\n"
            f"生成时间：{now}\n\n"
            f"股票：{stock_name}（{stock_code}）\n"
            f"风险等级：{risk_level}；影响评估：{impact}影响\n"
            f"监测到风险文章：{count}篇\n\n"
            "一、主要风险点\n"
            "1) 市场情绪转弱：负面声量上升，需关注股价压力\n"
            "2) 流动性风险：大额资金进出放大波动\n"
            "3) 基本面担忧：投资者对盈利与政策不确定性存疑\n\n"
            "二、建议\n"
            "- 短期：控制仓位，设置止损，关注成交量异常\n"
            "- 中期：跟踪公司澄清/公告与行业政策\n"
            "- 长期：重视基本面与现金流质量\n\n"
            "三、监控要点\n"
            "- 公司公告、监管问询、主力资金流向、同业情绪\n"
            "【自动生成，供风控参考】"
        )

    def _generate_mock_market_report(self, summary: Dict, market_context: str) -> str:
        now = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        return (
            f"《市场风险速报》\n生成时间：{now}\n"
            f"监测窗口：24h；风险事件：{summary.get('total', 0)} 起\n"
            f"高/中/低风险：{summary.get('high_risk',0)}/{summary.get('medium_risk',0)}/{summary.get('low_risk',0)}\n"
            f"涉及股票：{', '.join(summary.get('stocks', [])) or '—'}；行业：{', '.join(summary.get('industries', [])) or '—'}\n\n"
            "情绪观察：避险情绪升温，风险偏好下降；需防范短期放量下挫。\n"
            "操作建议：分散持仓、控制杠杆、跟踪公告与监管动向。\n"
            "监控信号：成交量激增、负面舆情再增、异常资金流。\n"
            "【自动生成，供内部风控参考】"
        )

    def _generate_error_briefing(self, stock_code: str, stock_name: str, error_msg: str) -> str:
        now = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        return (
            f"《风险简报生成失败通知》\n股票：{stock_name}（{stock_code}）\n时间：{now}\n"
            f"错误：{error_msg}\n请稍后重试或检查输入。"
        )


brief_generator = BriefGenerator(use_mock=True)
