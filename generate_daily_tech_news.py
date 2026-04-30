#!/usr/bin/env python3
"""Generate a daily markdown report: Top 10 tech events from previous day."""
from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
import re
import sys

import json
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "reports"))
TIMEZONE = os.getenv("TZ_NAME", "Asia/Shanghai")
MAX_ITEMS = int(os.getenv("MAX_ITEMS", "10"))


def now_local() -> dt.datetime:
    try:
        from zoneinfo import ZoneInfo

        return dt.datetime.now(ZoneInfo(TIMEZONE))
    except Exception:
        return dt.datetime.utcnow()


def previous_day_range(reference: dt.datetime) -> tuple[int, int, str]:
    prev_date = (reference - dt.timedelta(days=1)).date()
    start = dt.datetime.combine(prev_date, dt.time.min)
    end = dt.datetime.combine(prev_date, dt.time.max)

    try:
        from zoneinfo import ZoneInfo

        tz = ZoneInfo(TIMEZONE)
        start = start.replace(tzinfo=tz)
        end = end.replace(tzinfo=tz)
    except Exception:
        pass

    start_ts = int(start.timestamp())
    end_ts = int(end.timestamp())
    return start_ts, end_ts, prev_date.isoformat()


def fetch_hn_events(start_ts: int, end_ts: int, per_page: int = 50) -> list[dict]:
    url = "https://hn.algolia.com/api/v1/search_by_date"
    params = {
        "tags": "story",
        "numericFilters": f"created_at_i>{start_ts},created_at_i<{end_ts}",
        "hitsPerPage": per_page,
    }
    query = urlencode(params)
    try:
        with urlopen(f"{url}?{query}", timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
        hits = data.get("hits", [])
    except URLError:
        return []
    events = []
    for h in hits:
        title = (h.get("title") or "").strip()
        if not title:
            continue
        events.append(
            {
                "title": title,
                "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                "points": h.get("points") or 0,
                "comments": h.get("num_comments") or 0,
                "created_at": h.get("created_at") or "",
            }
        )
    events.sort(key=lambda x: (x["points"], x["comments"]), reverse=True)
    return events[:MAX_ITEMS]


def short_commentary(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ["openai", "anthropic", "llm", "ai", "model"]):
        return "AI赛道持续高热，关注其商业化落地与监管边界。"
    if any(k in t for k in ["apple", "google", "microsoft", "meta", "amazon", "tesla"]):
        return "巨头动作通常会重塑生态合作关系，短期看产品，中期看平台策略。"
    if any(k in t for k in ["security", "漏洞", "hack", "breach", "privacy"]):
        return "安全事件对品牌和合规影响直接，建议优先关注修复进展与披露透明度。"
    if any(k in t for k in ["chip", "nvidia", "amd", "intel", "semiconductor"]):
        return "算力与芯片仍是科技产业底层变量，供需变化会外溢到多个赛道。"
    return "这条新闻值得持续跟踪其后续数据与行业反馈，避免只看短期热度。"


def clean_filename(date_str: str) -> str:
    return re.sub(r"[^0-9\-]", "", date_str) + ".md"


def render_markdown(date_str: str, events: list[dict]) -> str:
    lines = []
    lines.append(f"# 科技圈十大事件日报（{date_str}）")
    lines.append("")
    lines.append("大家早上好，以下是前一天值得关注的科技圈十大事件：")
    lines.append("")

    if not events:
        lines.append("昨日暂无抓取到足够的高热科技新闻，建议人工补充。")
    else:
        for i, e in enumerate(events, start=1):
            lines.append(f"## {i}. {e['title']}")
            lines.append(f"- 链接：{e['url']}")
            lines.append(f"- 热度：{e['points']} 分 / {e['comments']} 评论")
            lines.append(f"- 简评：{short_commentary(e['title'])}")
            lines.append("")

    lines.append("---")
    lines.append("以上内容可直接用于公众号晨报推送，建议发布前补充与你业务相关的观点。")
    return "\n".join(lines)


def main() -> int:
    reference = now_local()
    start_ts, end_ts, date_str = previous_day_range(reference)
    events = fetch_hn_events(start_ts, end_ts)
    output = render_markdown(date_str, events)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / clean_filename(date_str)
    out_file.write_text(output, encoding="utf-8")
    print(f"Generated: {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
