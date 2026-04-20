"""
采集器基类.

定义数据采集器的抽象接口和通用功能.

Author: FDAS Team
Created: 2026-04-21
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd
import requests

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """
    数据采集器基类.

    所有数据采集器应继承此类并实现抽象方法.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化采集器.

        Args:
            config: 配置字典，如果为None则使用默认配置
        """
        self.config = config or {}
        self._initialize_from_config()

    def _initialize_from_config(self):
        """从配置字典初始化采集器参数."""
        # API配置
        api_config = self.config.get("api", {})
        self.api_url = api_config.get("base_url", "")
        self.api_method = api_config.get("method", "GET")
        self.timeout = api_config.get("timeout", 30)
        self.retry_config = api_config.get("retry", {})

        # 请求头配置
        self.headers = self.config.get("headers", {})

        # 请求参数配置
        self.params = self.config.get("params", {})

        # 货币对映射
        self.symbol_mapping = self.config.get("symbol_mapping", {})

        # 数据解析配置
        parser_config = self.config.get("data_parser", {})
        self.response_root = parser_config.get("response_root", "data")
        self.date_field = parser_config.get("date_field", 0)
        self.open_field = parser_config.get("open_field", 1)
        self.high_field = parser_config.get("high_field", 2)
        self.low_field = parser_config.get("low_field", 3)
        self.close_field = parser_config.get("close_field", 4)
        self.volume_field = parser_config.get("volume_field", 5)

    def get_symbol_mapping(self, symbol: str) -> str:
        """
        获取货币对映射后的代码.

        Args:
            symbol: 原始货币对代码

        Returns:
            映射后的代码，如果不存在映射则返回原始代码
        """
        return self.symbol_mapping.get(symbol, symbol)

    def _make_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
    ) -> requests.Response:
        """
        发起HTTP请求（带重试逻辑）.

        Args:
            url: 请求URL
            params: 请求参数
            headers: 请求头
            method: 请求方法

        Returns:
            响应对象

        Raises:
            requests.exceptions.RequestException: 请求失败
        """
        max_attempts = self.retry_config.get("max_attempt", 3)
        backoff_factor = self.retry_config.get("backoff_factor", 2)

        last_exception = None
        for attempt in range(max_attempts):
            try:
                if method.upper() == "GET":
                    response = requests.get(
                        url,
                        params=params,
                        headers=headers,
                        timeout=self.timeout,
                    )
                else:
                    response = requests.post(
                        url,
                        json=params,
                        headers=headers,
                        timeout=self.timeout,
                    )
                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    import time
                    wait_time = backoff_factor ** attempt
                    logger.warning(f"请求失败，{wait_time}秒后重试: {str(e)}")
                    time.sleep(wait_time)

        raise last_exception

    def _parse_kline_data(self, raw_data: list) -> pd.DataFrame:
        """
        解析K线数据.

        Args:
            raw_data: 原始K线数据列表

        Returns:
            DataFrame格式的数据
        """
        if not raw_data:
            return pd.DataFrame()

        parsed_data = []
        for kline in raw_data:
            try:
                fields = kline.split(",")
                parsed_data.append({
                    "date": fields[self.date_field],
                    "open": float(fields[self.open_field]),
                    "high": float(fields[self.high_field]),
                    "low": float(fields[self.low_field]),
                    "close": float(fields[self.close_field]),
                    "volume": float(fields[self.volume_field]) if len(fields) > self.volume_field else 0,
                })
            except (IndexError, ValueError) as e:
                logger.warning(f"解析K线数据失败: {str(e)}")
                continue

        return pd.DataFrame(parsed_data)

    @abstractmethod
    async def fetch_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        获取数据（抽象方法）.

        Args:
            symbol: 标的代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数

        Returns:
            DataFrame格式的数据
        """
        pass

    async def collect(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> dict:
        """
        采集数据并返回结果.

        Args:
            symbol: 标的代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数

        Returns:
            包含状态和数据的字典
        """
        try:
            df = await self.fetch_data(symbol, start_date, end_date, **kwargs)

            if df.empty:
                return {
                    "success": False,
                    "error": "未获取到数据",
                    "data": None,
                }

            return {
                "success": True,
                "data": df.to_dict(orient="records"),
                "count": len(df),
            }

        except Exception as e:
            logger.error(f"数据采集失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None,
            }