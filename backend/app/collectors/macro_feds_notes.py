"""
FEDS Notes 宏观数据采集器.

处理 longer-run-neutral (长期中性利率) 数据.
数据源: catalog.data.gov 数据集页面 -> 提取下载链接 -> 下载 CSV/Excel

Author: FDAS Team
Created: 2026-07-29
Updated: 2026-07-29 - 改为 HTML 页面抓取(API 已下线)
"""

import logging
import re
from io import BytesIO, StringIO
from typing import Any, Dict, List, Optional

import httpx
import pandas as pd
from bs4 import BeautifulSoup

from app.collectors.macro_base_collector import MacroBaseCollector

logger = logging.getLogger(__name__)


class MacroFEDSNotesCollector(MacroBaseCollector):
    """
    FEDS Notes 长期中性利率采集器.

    分两步:
    1. 抓取 catalog.data.gov 数据集页面
    2. 从页面提取实际数据文件 URL，下载并解析

    parse_config 关键字段:
        download_pattern: 数据文件 URL/格式匹配模式(如 "csv")
        frequency: 数据频率
        indicator_key: 指标键名
        multi_country: 是否为多国数据
    """

    async def _fetch_raw(self) -> bytes:
        """重写: 两步获取数据."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # 第一步: 获取数据集页面
            resp = await client.get(self.url, headers=self.headers)
            resp.raise_for_status()

            # 第二步: 从页面提取数据文件 URL
            data_url = self._extract_data_url(resp.content)
            if not data_url:
                raise ValueError("无法从页面中提取数据文件URL")

            # 处理相对 URL
            if data_url.startswith("/"):
                data_url = f"https://www.federalreserve.gov{data_url}"

            logger.info(f"[{self.source_code}] 数据文件URL: {data_url}")
            data_resp = await client.get(data_url, headers=self.headers)
            data_resp.raise_for_status()
            return data_resp.content

    def _extract_data_url(self, html: bytes) -> Optional[str]:
        """从 data.gov 数据集页面提取数据文件 URL."""
        soup = BeautifulSoup(html, "lxml")
        download_pattern = self.parse_config.get("download_pattern", "csv")

        # 查找包含数据文件 URL 的链接
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            text = a_tag.get_text(strip=True).lower()
            if download_pattern in href.lower() or download_pattern in text:
                return href

        # 回退: 查找所有以 csv/xlsx 结尾的链接
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if re.search(r"\.(csv|xlsx|xls)$", href, re.I):
                return href

        return None

    # 仅采集美国数据
    COUNTRY_CODES = ["US"]

    async def parse_raw(self, raw_data: bytes) -> pd.DataFrame:
        frequency = self.parse_config.get("frequency", "semi-annual")
        indicator_key = self.parse_config.get("indicator_key", self.source_code)

        # 尝试 CSV, 回退 Excel
        df = None
        try:
            df = pd.read_csv(BytesIO(raw_data))
        except Exception:
            try:
                df = pd.read_excel(BytesIO(raw_data))
            except Exception as e:
                raise ValueError(f"无法解析数据文件: {e}")

        if df is None or df.empty:
            logger.warning(f"[{self.source_code}] 数据文件为空")
            return pd.DataFrame()

        records = self._parse_wide_format(df, indicator_key, frequency)
        logger.info(f"[{self.source_code}] 解析完成: {len(records)} 条")
        return pd.DataFrame(records)

    def _parse_wide_format(self, df: pd.DataFrame, indicator_key: str, frequency: str) -> list:
        """解析宽表格式: date_h(如1960.0=H1, 1960.5=H2) + 国家代码列."""
        date_col = self._find_column(df, ["date_h", "date", "year", "period"])
        if not date_col:
            raise ValueError(f"无法识别日期列, 可用列: {list(df.columns)[:10]}")

        # 仅采集美国
        country_codes = self.COUNTRY_CODES

        records = []
        for _, row in df.iterrows():
            raw_date = row[date_col]
            if raw_date is None:
                continue

            # 解析半年度日期: 1960.0 → "1960-01-01", 1960.5 → "1960-07-01"
            try:
                year = int(raw_date)
                month_day = "-01-01" if (raw_date - year) < 0.1 else "-07-01"
                period_date = f"{year}{month_day}"
            except (ValueError, TypeError):
                period_date = str(raw_date)

            for cc in country_codes:
                if cc not in df.columns:
                    continue
                value = row[cc]
                if value is None or (isinstance(value, float) and pd.isna(value)):
                    continue

                records.append({
                    "country": cc,
                    "series_name": f"Longer-Run Neutral Rate {cc}",
                    "indicator_key": indicator_key,
                    "value": value,
                    "publish_date": None,
                    "period_date": period_date,
                    "frequency": frequency,
                })

        return records

    @staticmethod
    def _find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
        """查找第一个匹配的列名."""
        cols_lower = {c.lower(): c for c in df.columns}
        for c in candidates:
            if c in cols_lower:
                return cols_lower[c]
        return None
