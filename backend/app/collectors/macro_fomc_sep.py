"""
FOMC SEP 宏观数据采集器.

处理 r-sep (FOMC Summary of Economic Projections) 长期联邦基金利率预测.
数据源: FOMC 日历页面 → 历次 SEP 表格页面 → 提取 Federal funds rate LongRun Median

Author: FDAS Team
Created: 2026-07-29
Updated: 2026-07-29 - 遍历全部历史会议, 增强表格格式兼容性
"""

import asyncio
import logging
import re
from datetime import date
from typing import Optional

import httpx
import pandas as pd
from bs4 import BeautifulSoup

from app.collectors.macro_base_collector import MacroBaseCollector

logger = logging.getLogger(__name__)


class MacroFOMCSEPCollector(MacroBaseCollector):
    """FOMC SEP 采集器 — 全量历史 + 健壮表格解析."""

    async def parse_raw(self, raw_data: bytes) -> pd.DataFrame:
        return pd.DataFrame()

    async def collect(self, last_publish_date=None):
        frequency = self.parse_config.get("frequency", "by_meeting")
        country = self.parse_config.get("country", "US")

        # 第一步: 获取日历页, 提取全部唯一 SEP 链接
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(self.url, headers=self.headers)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.content, "lxml")
        meetings = sorted(set(
            m.group(1) for a in soup.find_all("a", href=True)
            if (m := re.search(r"fomcprojtabl(\d{8})\.htm", a["href"], re.I))
        ))
        if not meetings:
            raise ValueError("未在日历页找到任何 SEP 链接")

        logger.info(f"[{self.source_code}] 找到 {len(meetings)} 个历史会议 ({meetings[0]} ~ {meetings[-1]})")

        # 第二步: 逐个会议采集
        records = []
        sem = asyncio.Semaphore(3)  # 限制并发

        async def fetch_one(date_str: str):
            async with sem:
                pub_date = self._parse_date(date_str)
                url = f"https://www.federalreserve.gov/monetarypolicy/fomcprojtabl{date_str}.htm"
                try:
                    async with httpx.AsyncClient(timeout=30) as c:
                        r = await c.get(url, headers=self.headers)
                        r.raise_for_status()
                    value = self._extract_value(r.content)
                    if value is not None:
                        records.append({
                            "country": country,
                            "series_name": "SEP Federal Funds Rate Longer Run (Median)",
                            "indicator_key": "sep_median",
                            "value": value,
                            "publish_date": pub_date,
                            "period_date": pub_date,
                            "frequency": frequency,
                        })
                        logger.info(f"[{self.source_code}] {date_str}: {value}%")
                        return True
                    else:
                        logger.warning(f"[{self.source_code}] {date_str}: 未提取到值")
                        return False
                except Exception as e:
                    logger.warning(f"[{self.source_code}] {date_str} 失败: {e}")
                    return False

        tasks = [fetch_one(d) for d in meetings]
        await asyncio.gather(*tasks)

        logger.info(f"[{self.source_code}] 成功 {len(records)}/{len(meetings)} 个会议")

        if last_publish_date:
            before = len(records)
            records = [r for r in records if r.get("publish_date") and r["publish_date"] > last_publish_date]
            if before > len(records):
                logger.info(f"[{self.source_code}] 增量过滤: {before} -> {len(records)}")

        if records:
            return self._standardize(pd.DataFrame(records))
        return records

    def _extract_value(self, html: bytes) -> Optional[float]:
        """从 SEP 页面健壮提取 Federal funds rate Longer run Median."""
        soup = BeautifulSoup(html, "lxml")

        for table in soup.find_all("table"):
            text = table.get_text().lower()
            if "longer run" not in text:
                continue

            # 找到含 "Longer run" 的表头行, 确定列索引
            lr_col = None
            header_rows = []
            for tr in table.find_all("tr"):
                cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
                if any("longer run" in c.lower() for c in cells):
                    lr_col = next(i for i, c in enumerate(cells) if "longer run" in c.lower())
                    header_rows.append(cells)
                    break

            if lr_col is None:
                continue

            # 找 "Federal funds rate" 行 (大小写不敏感, 忽略前导空格)
            for tr in table.find_all("tr"):
                cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
                if not cells:
                    continue
                first = cells[0].lower().strip()
                if "federal funds rate" not in first:
                    continue
                if lr_col >= len(cells):
                    continue

                raw = cells[lr_col]
                return self._parse_value(raw)

        return None

    @staticmethod
    def _parse_value(raw: str) -> Optional[float]:
        """解析数值, 兼容范围格式(如 '3.0-3.5')取中值, 处理特殊字符."""
        if not raw:
            return None
        raw = raw.strip().replace("‹", "-").replace("–", "-").replace("—", "-")
        # 范围值取平均
        m = re.match(r"([\d.]+)\s*[-–]\s*([\d.]+)", raw)
        if m:
            try:
                return (float(m.group(1)) + float(m.group(2))) / 2
            except ValueError:
                pass
        # 单一数值
        try:
            return float(raw)
        except ValueError:
            pass
        return None

    @staticmethod
    def _parse_date(date_str: str) -> Optional[date]:
        try:
            return date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))
        except (ValueError, TypeError):
            return None
