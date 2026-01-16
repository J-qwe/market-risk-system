# 市场风险舆情API（Flask 版）

这是一个金融市场舆情风险挖掘系统的后端服务，提供简易浏览器落地页与 REST API：

- 根路径 `/`：简易网页界面，可加载新闻、查看仪表盘、生成风险应对简报。
- `/api/news`：新闻数据（含情感标签）。
- `/api/dashboard_data`：仪表盘统计（总数、风险占比等）。
- `/api/generate_brief`：根据选中新闻生成《风险应对简报》（当前为模拟）。

---

## 本地运行
```bash
pip install -r requirements.txt
python app.py
```
访问：`http://localhost:8000/`（网页界面）

---

## 线上访问（公开 URL）
- 根地址（落地页，直接可用）：https://risk-api-3c3n.onrender.com/
- 新闻数据：`https://risk-api-3c3n.onrender.com/api/news`
- 仪表盘：`https://risk-api-3c3n.onrender.com/api/dashboard_data`

提示：Render 免费实例若 15 分钟无访问会休眠，首次访问可能出现 30–60 秒唤醒延迟，耐心等待或多次刷新即可。

---

## 浏览器落地页说明
根路径 `/` 提供一个简易网页界面，支持：
- 加载新闻列表并选择风险新闻；
- 刷新仪表盘统计；
- 一键生成选中新闻的《风险应对简报》。

该页面直接调用同域 API，无需跨域配置，便于答辩演示与公开访问。

---

## 部署与更新
1. 推送代码到 GitHub：
```bash
git add .
git commit -m "feat: add landing page and docs"
git push origin main
```
2. Render 重新部署：进入服务页面，点击 “Manual Deploy → Deploy latest commit”。
3. 验证：访问根页面与上述 API 链接，确认功能正常。

---

## 后续接入建议
- 将 `mock_news_data` 替换为真实爬虫数据；
- 在生成简报端点接入本地/在线大模型（如 Ollama / OpenAI / 智谱等）；
- 如需前后端分离，可单独部署 Streamlit，并用 Nginx 反向代理将 `/` 指向前端、`/api/*` 指向后端，实现统一域名。
# 市场风险舆情API

这是一个金融市场舆情风险挖掘系统的后端API服务。

## 快速开始

### 本地运行
```bash
pip install -r requirements.txt
python main.py