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
        # 简易落地页，前端直接调用同域 API
        html = f"""
        <!doctype html>
        <html lang=zh-CN>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>市场舆情风险挖掘系统</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; margin: 0; background: #f7f7f9; color: #222; }}
                    header {{ background: #0d6efd; color: #fff; padding: 16px 24px; }}
                    h1 {{ margin: 0; font-size: 20px; }}
                    main {{ max-width: 1000px; margin: 24px auto; padding: 0 16px; }}
                    .card {{ background: #fff; border: 1px solid #e9ecef; border-radius: 8px; padding: 16px; margin-bottom: 16px; }}
                    .btn {{ display: inline-block; padding: 8px 12px; border-radius: 6px; border: 1px solid #0d6efd; color: #0d6efd; background: #fff; cursor: pointer; }}
                    .btn.primary {{ background: #0d6efd; color: #fff; border-color: #0d6efd; }}
                    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
                    .muted {{ color: #666; font-size: 12px; }}
                    ul {{ padding-left: 18px; }}
                    li.risk {{ color: #c1121f; }}
                    li.safe {{ color: #2b9348; }}
                    textarea {{ width: 100%; min-height: 120px; font-family: inherit; }}
                    .footer {{ margin-top: 24px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <header>
                    <h1>📈 市场舆情风险挖掘系统</h1>
                    <div class="muted">服务时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                </header>
                <main>
                    <div class="grid">
                        <section class="card">
                            <h3>新闻列表</h3>
                            <button class="btn" id="loadNews">加载新闻</button>
                            <ul id="newsList" style="margin-top: 12px;"></ul>
                        </section>
                        <section class="card">
                            <h3>仪表盘</h3>
                            <button class="btn" id="loadDash">刷新统计</button>
                            <div id="dash" class="muted" style="margin-top: 12px;">点击刷新统计数据</div>
                        </section>
                    </div>

                    <section class="card">
                        <h3>生成风险应对简报</h3>
                        <div class="muted">先在左侧选择一条风险新闻，再点击生成。</div>
                        <div style="margin-top: 12px;">
                            <button class="btn primary" id="genBrief">生成简报</button>
                        </div>
                        <div style="margin-top: 12px;">
                            <textarea id="briefOut" placeholder="生成的简报会显示在这里" readonly></textarea>
                        </div>
                    </section>

                    <section class="card">
                        <h3>接口快速测试</h3>
                        <ul>
                            <li><a href="/api/news" target="_blank">/api/news</a> 获取新闻数据</li>
                            <li><a href="/api/dashboard_data" target="_blank">/api/dashboard_data</a> 获取仪表盘数据</li>
                        </ul>
                    </section>

                    <div class="footer">Render 免费实例首次访问可能有唤醒延迟 30-60 秒。</div>
                </main>

                <script>
                    const base = window.location.origin;
                    let selectedNews = null;

                    async function fetchJSON(url, opts) {{
                        const res = await fetch(url, opts);
                        if (!res.ok) throw new Error(`HTTP ${res.status}`);
                        return await res.json();
                    }}

                    document.getElementById('loadNews').onclick = async () => {{
                        const listEl = document.getElementById('newsList');
                        listEl.innerHTML = '加载中...';
                        try {{
                            const data = await fetchJSON(`${base}/api/news`);
                            listEl.innerHTML = '';
                            if (!data || !data.length) {{
                                listEl.innerHTML = '<li class="muted">暂无新闻数据</li>';
                                return;
                            }}
                            data.forEach(item => {{
                                const li = document.createElement('li');
                                const isRisk = String(item.sentiment_label).toLowerCase() === 'negative';
                                li.className = isRisk ? 'risk' : 'safe';
                                li.style.cursor = 'pointer';
                                li.title = '点击选择用于生成简报';
                                li.textContent = `${{isRisk ? '⚠️' : '✅'}} ${{item.title}}`;
                                li.onclick = () => {{ selectedNews = item; [...listEl.children].forEach(el => el.style.fontWeight='normal'); li.style.fontWeight='bold'; }}
                                listEl.appendChild(li);
                            }});
                        }} catch (e) {{
                            listEl.innerHTML = `<li class="risk">加载失败：${{e.message}}</li>`;
                        }}
                    }};

                    document.getElementById('loadDash').onclick = async () => {{
                        const dash = document.getElementById('dash');
                        dash.textContent = '刷新中...';
                        try {{
                            const d = await fetchJSON(`${base}/api/dashboard_data`);
                            dash.innerHTML = `总新闻：<b>${{d.total_news}}</b>；风险新闻：<b>${{d.risk_news_count}}</b>；风险占比：<b>${{d.risk_ratio}}%</b><br/>最近更新时间：${{d.update_time}}`;
                        }} catch (e) {{ dash.textContent = `加载失败：${{e.message}}`; }}
                    }};

                    document.getElementById('genBrief').onclick = async () => {{
                        const out = document.getElementById('briefOut');
                        if (!selectedNews) {{ out.value = '请先在左侧列表选择一条新闻（⚠️为风险新闻）'; return; }}
                        out.value = '生成中...';
                        try {{
                            const body = {{ news_id: selectedNews.id, news_title: selectedNews.title, news_content: selectedNews.content || '' }};
                            const resp = await fetchJSON(`${base}/api/generate_brief`, {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(body) }});
                            out.value = `标题：${{resp.brief_title}}\n\n${{resp.brief_content}}\n\n生成时间：${{resp.generated_time}}`;
                        }} catch (e) {{ out.value = `生成失败：${{e.message}}`; }}
                    }};
                </script>
            </body>
        </html>
        """
        return html

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