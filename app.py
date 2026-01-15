from flask import Flask, jsonify, request
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 模拟数据
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
    }
]

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "市场风险舆情API", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

@app.route('/api/news', methods=['GET'])
def get_news():
    return jsonify(mock_news_data)

@app.route('/api/dashboard_data', methods=['GET'])
def get_dashboard():
    risk_news = [n for n in mock_news_data if n["sentiment_label"] == "negative"]
    return jsonify({
        "total_news": len(mock_news_data),
        "risk_news_count": len(risk_news),
        "risk_ratio": round(len(risk_news) / len(mock_news_data) * 100, 1),
        "avg_confidence": round(sum(n["confidence"] for n in risk_news) / len(risk_news), 3) if risk_news else 0,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/generate_brief', methods=['POST'])
def generate_brief():
    data = request.json if request.is_json else {}
    news_id = data.get('news_id', 1)
    news_title = data.get('news_title', '')
    
    return jsonify({
        "news_id": news_id,
        "brief_title": f"关于「{news_title}」的风险应对简报",
        "brief_content": f"【风险概述】检测到负面舆情：{news_title}\n【潜在影响】可能对相关股票价格产生短期冲击\n【应对建议】1. 监控股价异常波动 2. 关注公司后续公告\n【监控要点】成交量变化、相关行业政策动向",
        "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)