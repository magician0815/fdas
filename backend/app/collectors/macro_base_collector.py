"""
宏观数据采集器基类.

定义宏观数据采集器的统一接口：异步HTTP请求、数据解析、标准化、行哈希去重、增量过滤.

Author: FDAS Team
Created: 2026-07-29
"""

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
import pandas as pd
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class MacroBaseCollector(ABC):
    """
    宏观数据采集器基类.

    所有宏观数据采集器继承此类，实现 parse_raw() 方法即可.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.id = config.get("id")
        self.source_code = config.get("source_code", "")
        self.url = config.get("url", "")
        self.parse_config = config.get("parse_config", {})
        self.timeout = config.get("timeout_seconds", 60)
        self.request_method = config.get("request_method", "GET")
        self.headers = config.get("headers", {}) or {}
        self.retry_max = config.get("retry_max_attempts", 3)
        self.retry_backoff = config.get("retry_backoff_factor", 2.0)
        self.source_type = config.get("source_type", "")

    def _build_config_dict(self) -> Dict[str, Any]:
        """构建用于序列化的配置字典."""
        return {
            "id": str(self.id) if self.id else None,
            "source_code": self.source_code,
            "source_type": self.source_type,
            "url": self.url,
            "parse_config": self.parse_config,
            "timeout_seconds": self.timeout,
            "request_method": self.request_method,
            "headers": self.headers,
            "retry_max_attempts": self.retry_max,
        }

    async def _fetch_raw(self) -> bytes:
        """获取原始数据(bytes)，带 tenacity 重试."""

        @retry(
            stop=stop_after_attempt(self.retry_max),
            wait=wait_exponential(multiplier=1, min=2, max=30),
            retry=retry_if_exception_type((httpx.HTTPError, OSError)),
        )
        async def _do_fetch() -> bytes:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                method = self.request_method.upper()
                if method == "GET":
                    resp = await client.get(self.url, headers=self.headers)
                else:
                    resp = await client.post(self.url, headers=self.headers)
                resp.raise_for_status()
                return resp.content

        logger.info(f"[{self.source_code}] 开始请求: {self.url}")
        return await _do_fetch()

    @abstractmethod
    async def parse_raw(self, raw_data: bytes) -> pd.DataFrame:
        """
        解析原始数据为 DataFrame.

        子类实现具体的 Excel/HTML/JSON 解析逻辑.

        Returns:
            DataFrame 必须包含 publish_date, indicator_key, value 列
        """
        ...

    @staticmethod
    def _safe_float(val: Any) -> Optional[float]:
        if val is None:
            return None
        try:
            f = float(val)
            if pd.isna(f):
                return None
            return f
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_date(val: Any) -> Optional[date]:
        if val is None:
            return None
        if isinstance(val, date):
            return val
        try:
            dt = pd.to_datetime(val)
            # 修正两位数年份: pandas 将 67 解析为 2067, 应修正为 1967
            if dt.year > 2030:
                dt = dt.replace(year=dt.year - 100)
            return dt.date()
        except Exception:
            return None

    def _hash_row(self, row: Dict[str, Any]) -> str:
        """对一行数据标准化后进行 SHA-256 哈希，用于增量去重."""
        canonical = {
            "source_code": self.source_code,
            "indicator_key": row.get("indicator_key", ""),
            "period_date": str(row.get("period_date", "")),
            "publish_date": str(row.get("publish_date", "")),
            "value": str(row.get("value")),
            "country": row.get("country", ""),
        }
        raw = json.dumps(canonical, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _standardize(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        将解析后的 DataFrame 转换为标准 macro_data_points 记录格式.
        """
        records = []
        now = datetime.now(timezone.utc)

        for _, row in df.iterrows():
            pub_date = self._to_date(row.get("publish_date")) or now.date()
            per_date = self._to_date(row.get("period_date"))
            country = row.get("country")
            ikey = row.get("indicator_key", "")

            # 多国数据: indicator_key 附加国家后缀确保唯一性
            if country and country != "US":
                ikey = f"{ikey}_{country}"

            record = {
                "config_id": self.id,
                "source_code": self.source_code,
                "country": country,
                "series_name": row.get("series_name", self.source_code),
                "indicator_key": ikey,
                "value": self._safe_float(row.get("value")),
                "publish_date": pub_date,
                "period_date": per_date,
                "frequency": row.get("frequency", "quarterly"),
                "forecast_year": row.get("forecast_year"),
                "unit": row.get("unit", "percent"),
                "extra_info": row.get("metadata") or {},
            }
            record["raw_source_hash"] = self._hash_row(record)
            records.append(record)

        return records

    async def collect(self, last_publish_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        完整采集流程: fetch -> parse -> standardize -> 增量过滤.

        Args:
            last_publish_date: 上次采集的最大 publish_date，None 则全量采集

        Returns:
            标准化记录列表
        """
        raw = await self._fetch_raw()
        df = await self.parse_raw(raw)
        records = self._standardize(df)

        if last_publish_date:
            before = len(records)
            records = [r for r in records if r.get("publish_date") and r["publish_date"] > last_publish_date]
            logger.info(f"[{self.source_code}] 增量过滤: {before} -> {len(records)} 条, 截止 {last_publish_date}")

        logger.info(f"[{self.source_code}] 采集完成: {len(records)} 条记录")
        return records
