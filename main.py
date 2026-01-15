from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# 模拟数据
mock_news_data = [
    {
        "id": 1,
        "title": "某某科技发布业绩预警，预计季度亏损超5亿元",
        "content": "公司公告称受市场需求下滑影响...",
        "source": "东方财富",
        "publish_time": "2023-10-26 09:30:00",
        "sentiment_label": "negative",
        "confidence": 0.92,
        "stock_code": "300001.SZ"
    },
    {
        "id": 2,
        "title": "监管机构对某银行开展专项检查",
        "content": "据知情人士透露...",
        "source": "东方财富", 
        "publish_time": "2023-10-26 10:15:00",
        "sentiment_label": "negative",
        "confidence": 0.87,
        "stock_code": "601398.SH"
    }
]

@app.route('/')
def home():
    return "市场风险舆情API - 运行中"

@app.route('/api/news')
def get_news():
    return jsonify(mock_news_data)

@app.route('/api/dashboard_data')
def get_dashboard():
    risk_news = [n for n in mock_news_data if n["sentiment_label"] == "negative"]
    return jsonify({
        "total_news": len(mock_news_data),
        "risk_news_count": len(risk_news),
        "risk_ratio": round(len(risk_news) / len(mock_news_data) * 100, 1),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/generate_brief', methods=['POST'])
def generate_brief():
    # 简单模拟
    return jsonify({
        "news_id": 1,
        "brief_title": "风险应对简报",
        "brief_content": "检测到负面舆情，建议关注",
        "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)