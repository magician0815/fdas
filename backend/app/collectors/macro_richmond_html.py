"""
Richmond Fed HTML 宏观数据采集器.

处理 r-star-LM (Lubik-Matthes) 自然利率数据.
数据源: https://www.richmondfed.org/research/national_economy/natural_rate_interest

采集策略: 优先解析页内嵌入的 CSV 数据，回退到 HTML 表格解析.

Author: FDAS Team
Created: 2026-07-29
Updated: 2026-07-29 - 支持嵌入 CSV 数据提取
"""

import logging
from io import StringIO
from typing import Any, Dict

import pandas as pd
from bs4 import BeautifulSoup

from app.collectors.macro_base_collector import MacroBaseCollector

logger = logging.getLogger(__name__)


class MacroRichmondHTMLCollector(MacroBaseCollector):
    """
    Richmond Fed 宏观数据采集器.

    优先从页面嵌入元素提取 CSV 数据，回退到 HTML 表格解析.

    parse_config 关键字段:
        data_element_id: 嵌入数据的 HTML 元素 ID(如 "data-natural_rate_chart")
        date_format: 日期格式映射(将 "1-Jan-67" 转为标准格式)
        indicator_key: 指标键名
        frequency: 数据频率
        country: 国家
    """

    async def parse_raw(self, raw_data: bytes) -> pd.DataFrame:
        soup = BeautifulSoup(raw_data, "lxml")
        indicator_key = self.parse_config.get("indicator_key", self.source_code)
        frequency = self.parse_config.get("frequency", "quarterly")
        country = self.parse_config.get("country", "US")

        # 策略1: 尝试提取嵌入 CSV 数据
        data_element_id = self.parse_config.get("data_element_id", "data-natural_rate_chart")
        csv_element = soup.find(id=data_element_id)
        if csv_element:
            csv_text = csv_element.get_text().strip()
            if csv_text:
                return self._parse_csv(csv_text, indicator_key, frequency, country)

        # 策略2: 回退到 HTML 表格解析
        logger.info(f"[{self.source_code}] 未找到嵌入数据, 尝试表格解析")
        return self._parse_table(soup)

    def _parse_csv(self, csv_text: str, indicator_key: str, frequency: str, country: str) -> pd.DataFrame:
        """解析嵌入的 CSV 文本."""
        df = pd.read_csv(StringIO(csv_text))
        records = []

        for _, row in df.iterrows():
            date_val = row.get("dates", "")
            median = row.get("median")
            lower16 = row.get("lower16")
            upper84 = row.get("upper84")

            if not date_val:
                continue

            # 主指标: median 估计值
            if median is not None and not pd.isna(median):
                records.append({
                    "country": country,
                    "series_name": f"R_STAR_LM US (Median)",
                    "indicator_key": indicator_key,
                    "value": float(median),
                    "publish_date": None,
                    "period_date": date_val,
                    "frequency": frequency,
                    "metadata": {"confidence": "median", "lower16": float(lower16) if lower16 is not None and not pd.isna(lower16) else None, "upper84": float(upper84) if upper84 is not None and not pd.isna(upper84) else None},
                })

        logger.info(f"[{self.source_code}] CSV 解析完成: {len(records)} 条 (来自嵌入数据)")
        return pd.DataFrame(records)

    def _parse_table(self, soup: BeautifulSoup) -> pd.DataFrame:
        """回退方案: HTML 表格解析."""
        tables = soup.find_all("table")
        if not tables:
            raise ValueError("页面无表格且无嵌入CSV数据")

        col_mapping = self.parse_config.get("columns", {})
        indicator_key = self.parse_config.get("indicator_key", self.source_code)
        value_column = self.parse_config.get("value_column", "median")
        frequency = self.parse_config.get("frequency", "quarterly")
        country = self.parse_config.get("country", "US")
        skip_footnotes = self.parse_config.get("skip_footnotes", True)

        table_index = self.parse_config.get("table_index", 0)
        if table_index >= len(tables):
            raise ValueError(f"表格索引 {table_index} 超出范围, 页面共 {len(tables)} 个表格")

        table = tables[table_index]
        date_col_idx = col_mapping.get("date", 0)
        value_col_idx = col_mapping.get(value_column, 1)

        records = []
        rows = table.find_all("tr")
        for tr in rows:
            cells = tr.find_all(["td", "th"])
            cell_texts = [c.get_text(strip=True) for c in cells]
            if skip_footnotes and any(t.lower().startswith(("note", "source", "*")) for t in cell_texts):
                continue

            try:
                date_val = cell_texts[date_col_idx] if date_col_idx < len(cell_texts) else None
                value_val = cell_texts[value_col_idx] if value_col_idx < len(cell_texts) else None
                if not date_val or not value_val:
                    continue
                float(value_val)

                records.append({
                    "country": country,
                    "series_name": f"{indicator_key.upper()} US (LM)",
                    "indicator_key": indicator_key,
                    "value": value_val,
                    "publish_date": None,
                    "period_date": date_val,
                    "frequency": frequency,
                })
            except (ValueError, IndexError):
                continue

        logger.info(f"[{self.source_code}] 表格解析完成: {len(records)} 条")
        return pd.DataFrame(records)
