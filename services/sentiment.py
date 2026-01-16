"""
Sentiment analysis service
Simplified BERT-style analyzer using keyword heuristics for risk detection.
"""

import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Keyword-based sentiment analyzer with BERT-compatible interface."""

    def __init__(self, use_simple_mode: bool = True):
        self.use_simple_mode = use_simple_mode
        self.model_loaded = True  # simplified: always ready
        self.status = {
            "model_loaded": self.model_loaded,
            "use_simple_mode": use_simple_mode,
            "analyzed_count": 0,
        }
        self.risk_keywords = [
            "下跌", "暴跌", "亏损", "下滑", "下降", "预警", "风险", "违规",
            "调查", "诉讼", "处罚", "警告", "退市", "ST", "*ST", "问询",
            "监管", "爆雷", "债务", "违约", "破产", "重组", "裁员", "危机",
            "利空", "跌停", "破发", "破净", "减持", "质押", "冻结", "查封",
            "降价", "松动", "洗牌", "困境", "降价潮", "压力", "回调", "垃圾",
            "割肉", "被套", "跌停板", "一泻千里", "崩盘", "腰斩", "凉凉",
            "完蛋", "危险", "套牢", "割韭菜", "暴雷", "踩雷", "黑天鹅",
        ]
        self.positive_keywords = [
            "上涨", "大涨", "增长", "盈利", "利好", "突破", "创新", "新高",
            "合作", "签约", "中标", "扩产", "增产", "获奖", "表彰", "优秀",
            "领先", "升级", "转型", "复苏", "反弹", "回暖", "改善", "提升",
            "优化", "机会", "涨停", "翻倍", "增持", "回购", "分红", "送转",
            "业绩", "预增", "政策", "支持", "牛市", "上板", "发财", "空间",
        ]
        self.neutral_keywords = [
            "维持", "平稳", "稳定", "观望", "调整", "整理", "横盘", "持平",
            "中性", "一般", "普通", "正常", "常规", "预计", "预期", "可能",
            "或许", "大概", "估计", "猜测", "推测",
        ]

    def analyze(self, text: str, title: str = "") -> Dict:
        if not text:
            return self._create_empty_result()
        full_text = f"{title} {text}".lower()
        if self.use_simple_mode:
            result = self._analyze_with_keywords(full_text)
        else:
            result = self._analyze_with_keywords(full_text)
        self.status["analyzed_count"] += 1
        return result

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        return [self.analyze(t) for t in texts]

    def _analyze_with_keywords(self, text: str) -> Dict:
        risk_count = sum(1 for w in self.risk_keywords if w in text)
        positive_count = sum(1 for w in self.positive_keywords if w in text)
        neutral_count = sum(1 for w in self.neutral_keywords if w in text)
        total = risk_count + positive_count + neutral_count

        if total > 0:
            score = (
                positive_count * 1.0
                + neutral_count * 0.0
                - risk_count * 1.5
            ) / total
            score = max(-1.0, min(1.0, score))
            confidence = min(0.95, 0.6 + min(total, 5) * 0.08)
        else:
            score = 0.0
            confidence = 0.5

        if score < -0.3:
            label = "风险"
        elif score > 0.3:
            label = "正面"
        else:
            label = "中性"

        return {
            "success": True,
            "text": text[:100] + "..." if len(text) > 100 else text,
            "sentiment_score": round(score, 3),
            "sentiment_label": label,
            "confidence": round(confidence, 3),
            "keyword_counts": {
                "risk": risk_count,
                "positive": positive_count,
                "neutral": neutral_count,
                "total": total,
            },
            "method": "keyword_matching",
            "analysis_time": datetime.now().isoformat(),
        }

    def _create_empty_result(self) -> Dict:
        return {
            "success": False,
            "text": "",
            "sentiment_score": 0.0,
            "sentiment_label": "中性",
            "confidence": 0.0,
            "keyword_counts": {"risk": 0, "positive": 0, "neutral": 0, "total": 0},
            "method": "none",
            "error": "输入文本为空",
            "analysis_time": datetime.now().isoformat(),
        }

    def get_status(self) -> Dict:
        return self.status.copy()


sentiment_analyzer = SentimentAnalyzer(use_simple_mode=True)


def analyze_text(text: str, title: str = "") -> Dict:
    return sentiment_analyzer.analyze(text, title)


def analyze_batch(texts: List[str]) -> List[Dict]:
    return sentiment_analyzer.analyze_batch(texts)
