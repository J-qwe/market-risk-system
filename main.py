from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="市场风险舆情API", description="模拟数据接口")

# 允许前端跨域访问（重要！）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 定义数据结构（Day0契约）
class NewsItem(BaseModel):
    id: int
    title: str
    content: str
    source: str = "东方财富"
    publish_time: str
    sentiment_label: str  # "positive", "negative", "neutral"
    confidence: float
    stock_code: str = "000001.SZ"

class BriefRequest(BaseModel):
    news_id: int
    news_title: str
    news_content: str

class BriefResponse(BaseModel):
    news_id: int
    brief_title: str
    brief_content: str
    generated_time: str

# 2. 硬编码模拟数据
mock_news_data = [
    {
        "id": 1,
        "title": "某某科技发布业绩预警，预计季度亏损超5亿元",
        "content": "公司公告称受市场需求下滑影响，主要产品线销售额大幅下降...",
        "source": "东方财富",
        "publish_time": "2023-10-26 09:30:00",
        "sentiment_label": "negative",
        "confidence": 0.92,
        "stock_code": "300001.SZ"
    },
    {
        "id": 2,
        "title": "监管机构对某银行开展专项检查，涉及违规放贷问题",
        "content": "据知情人士透露，此次检查重点针对房地产相关贷款业务...",
        "source": "东方财富",
        "publish_time": "2023-10-26 10:15:00",
        "sentiment_label": "negative",
        "confidence": 0.87,
        "stock_code": "601398.SH"
    },
    {
        "id": 3,
        "title": "新能源板块集体回调，龙头股单日下跌超8%",
        "content": "今日新能源板块普遍走低，市场分析认为与产能过剩担忧有关...",
        "source": "东方财富",
        "publish_time": "2023-10-26 11:20:00",
        "sentiment_label": "negative",
        "confidence": 0.78,
        "stock_code": "002594.SZ"
    },
    {
        "id": 4,
        "title": "多家券商发布看涨报告，看好消费复苏主线",
        "content": "随着政策利好持续释放，大消费板块近期获得机构集中推荐...",
        "source": "东方财富",
        "publish_time": "2023-10-26 13:45:00",
        "sentiment_label": "positive",
        "confidence": 0.65,
        "stock_code": "600519.SH"
    }
]

# 3. 实现三个核心API（完全按照Day0约定）
@app.get("/api/news", response_model=List[NewsItem])
async def get_news():
    """获取新闻列表（带情感分析结果）"""
    return mock_news_data

@app.post("/api/generate_brief", response_model=BriefResponse)
async def generate_brief(request: BriefRequest):
    """生成风险简报（模拟）"""
    return {
        "news_id": request.news_id,
        "brief_title": f"关于「{request.news_title}」的风险应对简报",
        "brief_content": f"【风险概述】检测到负面舆情：{request.news_title}\n【潜在影响】可能对相关股票价格产生短期冲击，建议关注\n【应对建议】1. 监控股价异常波动 2. 关注公司后续公告 3. 评估持仓风险\n【监控要点】成交量变化、相关行业政策动向",
        "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/dashboard_data")
async def get_dashboard_data():
    """获取仪表盘统计数据"""
    risk_news = [n for n in mock_news_data if n["sentiment_label"] == "negative"]
    
    # 简单风险词频统计（模拟）
    risk_keywords = ["下跌", "亏损", "风险", "违规", "危机", "下跌", "诉讼", "预警"]
    
    return {
        "total_news": len(mock_news_data),
        "risk_news_count": len(risk_news),
        "risk_ratio": round(len(risk_news) / len(mock_news_data) * 100, 1),
        "avg_confidence": round(sum(n["confidence"] for n in risk_news) / len(risk_news), 3) if risk_news else 0,
        "top_risk_stocks": list(set([n["stock_code"] for n in risk_news])),
        "risk_keyword_freq": {word: 3 for word in risk_keywords[:5]},  # 模拟词频
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# 本地测试用
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)