from flask import Flask, jsonify, request
import os
from datetime import datetime
from flask_cors import CORS

from services.pipeline import (
    load_news,
    analyze_news,
    compute_dashboard,
    generate_alerts,
    run_pipeline,
    get_data_source_info,
)
from services.brief import brief_generator
from services.sentiment import sentiment_analyzer

app = Flask(__name__)
CORS(app)

def _current_news():
    return analyze_news(load_news())

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
                    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&display=swap');
                    body {{ font-family: 'Manrope', 'Helvetica Neue', sans-serif; margin: 0; background: linear-gradient(180deg, #f4f6fb 0%, #f9fafc 60%, #ffffff 100%); color: #1f2a44; }}
                    header {{ background: #0d6efd; color: #fff; padding: 16px 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
                    h1 {{ margin: 0; font-size: 20px; letter-spacing: 0.4px; }}
                    main {{ max-width: 1100px; margin: 24px auto; padding: 0 16px 32px; }}
                    .card {{ background: #fff; border: 1px solid #e9ecef; border-radius: 10px; padding: 16px; margin-bottom: 16px; box-shadow: 0 6px 20px rgba(0,0,0,0.05); }}
                    .btn {{ display: inline-block; padding: 9px 14px; border-radius: 8px; border: 1px solid #0d6efd; color: #0d6efd; background: #fff; cursor: pointer; font-weight: 600; transition: all 0.2s ease; }}
                    .btn.primary {{ background: #0d6efd; color: #fff; border-color: #0d6efd; }}
                    .btn:hover {{ transform: translateY(-1px); box-shadow: 0 6px 16px rgba(13,110,253,0.15); }}
                    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
                    .muted {{ color: #6c757d; font-size: 12px; }}
                    ul {{ padding-left: 18px; }}
                    li.risk {{ color: #c1121f; }}
                    li.safe {{ color: #2b9348; }}
                    textarea {{ width: 100%; min-height: 120px; font-family: inherit; border-radius: 8px; border: 1px solid #e2e6ea; padding: 10px; background: #fbfcfe; }}
                    .footer {{ margin-top: 24px; color: #6c757d; font-size: 12px; text-align: center; }}
                    .pill {{ display: inline-block; padding: 4px 8px; border-radius: 999px; font-size: 11px; background: #eef2ff; color: #0d6efd; margin-left: 6px; }}
                    .stack {{ display: grid; gap: 8px; }}
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
                            <h3>新闻列表 <span class="pill">实时情感</span></h3>
                            <div class="stack">
                                <button class="btn" id="loadNews">加载新闻</button>
                                <small class="muted">点击新闻即可选中用于生成简报</small>
                            </div>
                            <ul id="newsList" style="margin-top: 12px;"></ul>
                        </section>
                        <section class="card">
                            <h3>仪表盘</h3>
                            <div class="stack">
                                <button class="btn" id="loadDash">刷新统计</button>
                                <div id="dash" class="muted">点击刷新统计数据</div>
                            </div>
                        </section>
                    </div>

                    <section class="card">
                        <h3>自动预警 + 市场简报</h3>
                        <div class="stack">
                            <div class="muted">一键跑通：情感判别 → 风险报警 → 风险简报/市场速报。</div>
                            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                                <button class="btn primary" id="runPipeline">一键检测+简报</button>
                                <button class="btn" id="genBrief">仅对选中新闻生成简报</button>
                            </div>
                            <textarea id="briefOut" placeholder="生成的风险应对简报会显示在这里" readonly></textarea>
                            <textarea id="marketReport" placeholder="市场风险速报将显示在这里" readonly></textarea>
                        </div>
                    </section>

                    <section class="card">
                        <h3>自动报警列表</h3>
                        <div class="stack">
                            <div class="muted">当情感为风险且置信度≥0.6时触发。</div>
                            <ul id="alertsList" style="margin-top: 6px;"></ul>
                        </div>
                    </section>

                    <section class="card">
                        <h3>接口快速测试</h3>
                        <ul>
                            <li><a href="/api/news" target="_blank">/api/news</a> 获取新闻数据</li>
                            <li><a href="/api/dashboard_data" target="_blank">/api/dashboard_data</a> 获取仪表盘数据</li>
                            <li><a href="/api/pipeline" target="_blank">/api/pipeline</a> 一键跑全流程</li>
                        </ul>
                    </section>

                    <div class="footer">Render 免费实例首次访问可能有唤醒延迟 30-60 秒。</div>
                </main>

                <script>
                    const base = window.location.origin;
                    let selectedNews = null;

                    async function fetchJSON(url, opts) {{
                        const res = await fetch(url, opts);
                        if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
                        return await res.json();
                    }}

                    document.getElementById('loadNews').onclick = async () => {{
                        const listEl = document.getElementById('newsList');
                        listEl.innerHTML = '加载中...';
                        try {{
                            const data = await fetchJSON(`${{base}}/api/news`);
                            listEl.innerHTML = '';
                            if (!data || !data.length) {{
                                listEl.innerHTML = '<li class="muted">暂无新闻数据</li>';
                                return;
                            }}
                            data.forEach(item => {{
                                const li = document.createElement('li');
                                const isRisk = String(item.sentiment_label).includes('风险');
                                li.className = isRisk ? 'risk' : 'safe';
                                li.style.cursor = 'pointer';
                                li.title = '点击选择用于生成简报';
                                const badge = isRisk ? '⚠️' : '✅';
                                const stock = item.stock_code ? ` ｜ ${{item.stock_code}}` : '';
                                li.textContent = `${{badge}} ${{item.title}}${{stock}}`;
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
                            const d = await fetchJSON(`${{base}}/api/dashboard_data`);
                            dash.innerHTML = `总新闻：<b>${{d.total_news}}</b>；风险：<b>${{d.risk_news_count}}</b>；风险占比：<b>${{d.risk_ratio}}%</b>；警报：<b>${{d.alert_count}}</b><br/>高/中风险：<b>${{d.high_risk}}</b>/<b>${{d.medium_risk}}</b>；风险关键词命中：<b>${{d.keyword_hits}}</b><br/>最近更新时间：${{d.update_time}}`;
                        }} catch (e) {{ dash.textContent = `加载失败：${{e.message}}`; }}
                    }};

                    document.getElementById('runPipeline').onclick = async () => {{
                        const out = document.getElementById('briefOut');
                        const report = document.getElementById('marketReport');
                        const alerts = document.getElementById('alertsList');
                        const dash = document.getElementById('dash');
                        const listEl = document.getElementById('newsList');
                        out.value = '生成中...';
                        report.value = '生成中...';
                        alerts.innerHTML = '检测中...';
                        dash.textContent = '刷新中...';
                        try {{
                            const resp = await fetchJSON(`${{base}}/api/pipeline`);
                            // 更新新闻
                            listEl.innerHTML = '';
                            resp.news.forEach(item => {{
                                const li = document.createElement('li');
                                const isRisk = item.is_risk;
                                li.className = isRisk ? 'risk' : 'safe';
                                li.style.cursor = 'pointer';
                                const badge = isRisk ? '⚠️' : '✅';
                                li.textContent = `${{badge}} ${{item.title}}`;
                                li.onclick = () => {{ selectedNews = item; [...listEl.children].forEach(el => el.style.fontWeight='normal'); li.style.fontWeight='bold'; }}
                                listEl.appendChild(li);
                            }});
                            // 更新仪表盘
                            const d = resp.dashboard;
                            dash.innerHTML = `总新闻：<b>${{d.total_news}}</b>；风险：<b>${{d.risk_news_count}}</b>；风险占比：<b>${{d.risk_ratio}}%</b>；警报：<b>${{d.alert_count}}</b><br/>高/中风险：<b>${{d.high_risk}}</b>/<b>${{d.medium_risk}}</b>；风险关键词命中：<b>${{d.keyword_hits}}</b><br/>最近更新时间：${{d.update_time}}`;
                            // 报警
                            alerts.innerHTML = '';
                            if (!resp.alerts.length) {{
                                alerts.innerHTML = '<li class="muted">暂无触发的警报</li>';
                            }} else {{
                                resp.alerts.forEach(a => {{
                                    const li = document.createElement('li');
                                    li.className = 'risk';
                                    li.textContent = `⚠️ ${{a.title}} ｜ 置信度 ${{a.confidence}} ｜ 分数 ${{a.sentiment_score}}`;
                                    alerts.appendChild(li);
                                }});
                            }}
                            // 简报与市场速报
                            out.value = resp.risk_brief || '未生成';
                            report.value = resp.market_report || '未生成';
                        }} catch (e) {{
                            out.value = `生成失败：${{e.message}}`;
                            report.value = '';
                            alerts.innerHTML = `<li class="risk">流水线失败：${{e.message}}</li>`;
                            dash.textContent = '流水线失败';
                        }}
                    }};

                    document.getElementById('genBrief').onclick = async () => {{
                        const out = document.getElementById('briefOut');
                        if (!selectedNews) {{ out.value = '请先在左侧列表选择一条新闻（⚠️为风险新闻）'; return; }}
                        out.value = '生成中...';
                        try {{
                            const body = {{ news_id: selectedNews.id, news_title: selectedNews.title, news_content: selectedNews.content || '' }};
                            const resp = await fetchJSON(`${{base}}/api/generate_brief`, {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(body) }});
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
    return jsonify(_current_news())

@app.route('/api/dashboard_data', methods=['GET'])
def get_dashboard():
    processed = _current_news()
    dash = compute_dashboard(processed)
    return jsonify(dash)

@app.route('/api/generate_brief', methods=['POST'])
def generate_brief():
    data = request.json if request.is_json else {}
    news_id = data.get('news_id', 1)
    news_title = data.get('news_title', '')
    news_content = data.get('news_content', '')
    stock_code = data.get('stock_code', '000000')
    stock_name = data.get('stock_name', '自选标的')
    articles = [f"{news_title} {news_content}".strip()] if (news_title or news_content) else [news_title]
    brief_text = brief_generator.generate_risk_briefing(stock_code, stock_name, articles)
    return jsonify({
        "news_id": news_id,
        "brief_title": f"关于「{news_title}」的风险应对简报",
        "brief_content": brief_text,
        "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route('/api/pipeline', methods=['GET'])
def pipeline_run():
    result = run_pipeline()
    return jsonify(result)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})


@app.route('/api/source_info', methods=['GET'])
def source_info():
    return jsonify(get_data_source_info())

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=False)