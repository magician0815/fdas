"""
FRED CSV 宏观数据采集器.

通过 FRED (Federal Reserve Economic Data) CSV 端点获取经济指标数据。
通用设计, 通过 parse_config 配置不同的指标 (real_gdp / potential_gdp 等).

Author: FDAS Team
Created: 2026-07-29
"""

import logging
from io import StringIO
from typing import Any, Dict, List

import httpx
import pandas as pd

from app.collectors.macro_base_collector import MacroBaseCollector

logger = logging.getLogger(__name__)


class MacroFREDCSVCollector(MacroBaseCollector):
    """
    FRED CSV 通用采集器.

    parse_config 关键字段:
        url_template: URL 模板, {sid} 替换为实际序列ID
        sid: FRED 序列 ID (如 GDPC1, GDPPOT)
        date_col: CSV 日期列名 (observation_date)
        value_col: CSV 数值列名 (通常与 sid 相同)
        frequency: 数据频率 (quarterly/monthly)
        unit: 数据单位
        indicator_key: 指标键名 (real_gdp / potential_gdp)
    """

    async def _fetch_raw(self) -> bytes:
        """重写: 直接通过 FRED CSV 端点获取."""
        url_template = self.parse_config.get("url_template",
            "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}")
        sid = self.parse_config.get("sid", "")
        url = url_template.replace("{sid}", sid)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.content

    async def parse_raw(self, raw_data: bytes) -> pd.DataFrame:
        indicator_key = self.parse_config.get("indicator_key", self.source_code)
        frequency = self.parse_config.get("frequency", "quarterly")
        unit = self.parse_config.get("unit", "")
        date_col = self.parse_config.get("date_col", "observation_date")
        value_col = self.parse_config.get("value_col", self.parse_config.get("sid", ""))

        df = pd.read_csv(StringIO(raw_data.decode("utf-8")))
        if df.empty:
            logger.warning(f"[{self.source_code}] CSV 为空")
            return pd.DataFrame()

        if date_col not in df.columns:
            raise ValueError(f"日期列 '{date_col}' 不在 CSV 中: {list(df.columns)}")
        if value_col not in df.columns:
            raise ValueError(f"数值列 '{value_col}' 不在 CSV 中: {list(df.columns)}")

        records = []
        for _, row in df.iterrows():
            date_val = row[date_col]
            value = row[value_col]
            if date_val is None or (isinstance(value, float) and pd.isna(value)):
                continue

            records.append({
                "country": "US",
                "series_name": f"{indicator_key.upper()}",
                "indicator_key": indicator_key,
                "value": float(value),
                "publish_date": None,
                "period_date": str(date_val),
                "frequency": frequency,
                "unit": unit,
            })

        logger.info(f"[{self.source_code}] FRED CSV 解析: {len(records)} 条")
        return pd.DataFrame(records)
