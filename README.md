# 每日科技圈十大事件自动生成

这个仓库可以在每天早上 9 点，自动生成“前一天科技圈十大事件”Markdown 文件，并按日期命名，便于直接复制到微信公众号。

## 功能

- 抓取前一天的科技热点（默认来源：Hacker News 数据接口）
- 按热度排序，输出前 10 条
- 每条包含：标题、链接、热度、简评
- 输出文件为 `reports/YYYY-MM-DD.md`

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 generate_daily_tech_news.py
```

生成结果示例：

- `reports/2026-04-29.md`

## 定时任务（每天早上 9 点）

> 默认时区按 `Asia/Shanghai` 处理“前一天”日期。

编辑 crontab：

```bash
crontab -e
```

加入下面一行（每天 09:00 执行）：

```cron
0 9 * * * cd /workspace/daily-tech-news && /usr/bin/env TZ_NAME=Asia/Shanghai OUTPUT_DIR=reports /usr/bin/python3 generate_daily_tech_news.py >> /workspace/daily-tech-news/daily.log 2>&1
```

## 输出格式（可直接发公众号）

脚本会生成以下结构：

- 标题：`科技圈十大事件日报（YYYY-MM-DD）`
- 导语
- 1~10 条事件
  - 链接
  - 热度（分数/评论）
  - 简评（可二次编辑成你的观点）

## 可选改造

- 换成你自己的新闻源（如 RSS、行业站点 API）
- 用大模型接口增强“简评”质量
- 增加“关键词过滤（如 AI/芯片/出海）”
