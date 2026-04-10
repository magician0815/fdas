"""
AKShare数据采集器.

使用AKShare库采集金融数据，支持forex_hist接口.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-10 - 适配ForexSymbol和ForexDaily模型
"""

from typing import List, Dict, Optional
from datetime import date
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
import asyncio

logger = logging.getLogger(__name__)


class AKShareCollector:
    """
    AKShare数据采集器.

    使用AKShare库采集外汇数据，支持重试机制.
    """

    async def fetch_supported_symbols(self) -> List[Dict]:
        """
        获取支持的货币对列表.

        从AKShare获取外汇货币对列表，返回中文名称和英文代码.

        Returns:
            List[Dict]: 货币对列表，格式为 [{"value": "美元人民币", "code": "USDCNY", "label": "美元人民币(USDCNY)"}]
        """
        logger.info("获取AKShare支持的货币对列表")

        try:
            # 在线程池中执行同步的AKShare调用
            symbols = await asyncio.to_thread(
                self._fetch_forex_symbols,
            )

            logger.info(f"获取到 {len(symbols)} 个货币对")
            return symbols

        except Exception as e:
            logger.error(f"获取货币对列表失败: {str(e)}")
            # 返回默认列表作为备用
            return self._get_default_symbols()

    def _fetch_forex_symbols(self) -> List[Dict]:
        """
        同步获取AKShare外汇货币对列表.

        Returns:
            List[Dict]: 货币对列表
        """
        try:
            import akshare as ak
        except ImportError:
            logger.warning("AKShare库未安装，使用默认货币对列表")
            return self._get_default_symbols()

        try:
            # 尝试获取外汇货币对列表
            # AKShare forex_symbols接口返回货币对信息
            df = ak.forex_symbols()

            symbols = []
            for _, row in df.iterrows():
                name = row.get("name", "")
                code = row.get("code", "")

                if name and code:
                    symbols.append({
                        "value": name,  # 中文名称
                        "code": code,   # 英文代码
                        "label": f"{name}({code})",
                    })

            return symbols

        except Exception as e:
            logger.warning(f"获取forex_symbols失败: {str(e)}，使用默认列表")
            return self._get_default_symbols()

    def _get_default_symbols(self) -> List[Dict]:
        """
        返回默认货币对列表.

        当AKShare接口无法获取时使用此列表.

        Returns:
            List[Dict]: 默认货币对列表
        """
        default_symbols = [
            {"value": "美元人民币", "code": "USDCNY", "label": "美元人民币(USDCNY)"},
            {"value": "欧元美元", "code": "EURUSD", "label": "欧元美元(EURUSD)"},
            {"value": "英镑美元", "code": "GBPUSD", "label": "英镑美元(GBPUSD)"},
            {"value": "美元日元", "code": "USDJPY", "label": "美元日元(USDJPY)"},
            {"value": "美元港币", "code": "USDHKD", "label": "美元港币(USDHKD)"},
            {"value": "美元瑞郎", "code": "USDCHF", "label": "美元瑞郎(USDCHF)"},
            {"value": "澳元美元", "code": "AUDUSD", "label": "澳元美元(AUDUSD)"},
            {"value": "新西兰元美元", "code": "NZDUSD", "label": "新西兰元美元(NZDUSD)"},
            {"value": "美元加元", "code": "USDCAD", "label": "美元加元(USDCAD)"},
            {"value": "美元新加坡元", "code": "USDSGD", "label": "美元新加坡元(USDSGD)"},
            {"value": "欧元人民币", "code": "EURCNY", "label": "欧元人民币(EURCNY)"},
            {"value": "英镑人民币", "code": "GBPCNY", "label": "英镑人民币(GBPCNY)"},
            {"value": "日元人民币", "code": "JPYCNY", "label": "日元人民币(JPYCNY)"},
            {"value": "港币人民币", "code": "HKDCNY", "label": "港币人民币(HKDCNY)"},
            {"value": "欧元英镑", "code": "EURGBP", "label": "欧元英镑(EURGBP)"},
            {"value": "欧元日元", "code": "EURJPY", "label": "欧元日元(EURJPY)"},
            {"value": "英镑日元", "code": "GBPJPY", "label": "英镑日元(GBPJPY)"},
            {"value": "澳元日元", "code": "AUDJPY", "label": "澳元日元(AUDJPY)"},
            {"value": "欧元澳元", "code": "EURAUD", "label": "欧元澳元(EURAUD)"},
            {"value": "欧元加元", "code": "EURCAD", "label": "欧元加元(EURCAD)"},
        ]
        return default_symbols

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def collect_forex_hist(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        采集外汇日线行情数据.

        调用AKShare forex_hist接口获取历史数据.

        Args:
            symbol_name: 货币对名称（中文，如"美元人民币"，用于AKShare接口）
            symbol_code: 货币对代码（英文，如"USDCNY"，用于数据库存储）
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            List[Dict]: 汇率数据列表，格式适配数据库存储

        Raises:
            Exception: 采集失败（重试3次后抛出）
        """
        logger.info(f"开始采集外汇数据: {symbol_name} ({symbol_code}), {start_date} ~ {end_date}")

        try:
            # 在线程池中执行同步的AKShare调用
            df = await asyncio.to_thread(
                self._call_forex_hist,
                symbol_name,
                start_date,
                end_date,
            )

            if df is None or df.empty:
                logger.warning(f"采集数据为空: {symbol_name}")
                return []

            # 转换数据格式
            records = self._transform_data(df, symbol_code)

            logger.info(f"成功采集 {len(records)} 条 {symbol_name} 数据")
            return records

        except Exception as e:
            logger.error(f"采集外汇数据失败: {str(e)}")
            raise

    def _call_forex_hist(
        self,
        symbol_name: str,
        start_date: date,
        end_date: date,
    ):
        """
        同步调用AKShare forex_hist接口.

        Args:
            symbol_name: 货币对名称（中文）
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame: AKShare返回的数据
        """
        try:
            import akshare as ak
        except ImportError:
            logger.error("AKShare库未安装，请运行: pip install akshare")
            raise ImportError("AKShare库未安装")

        # 转换日期格式为YYYYMMDD字符串
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")

        logger.debug(f"调用forex_hist接口: symbol={symbol_name}, start={start_str}, end={end_str}")

        # 调用forex_hist接口（使用中文货币对名称）
        df = ak.forex_hist(
            symbol=symbol_name,
            start_date=start_str,
            end_date=end_str,
        )

        return df

    def _transform_data(
        self,
        df,
        symbol_code: str,
    ) -> List[Dict]:
        """
        转换数据格式.

        将AKShare返回的DataFrame转换为数据库存储格式.

        Args:
            df: 原始DataFrame（AKShare返回）
            symbol_code: 货币对代码（英文）

        Returns:
            List[Dict]: 转换后的数据列表
        """
        import pandas as pd

        records = []

        # AKShare forex_hist返回字段：
        # 日期、开盘价、收盘价、最高价、最低价、成交量、涨跌幅、涨跌额、振幅
        for _, row in df.iterrows():
            # 处理日期字段
            raw_date = row.get("日期")
            if isinstance(raw_date, str):
                try:
                    from datetime import datetime
                    trade_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
                except ValueError:
                    trade_date = datetime.strptime(raw_date, "%Y%m%d").date()
            elif isinstance(raw_date, pd.Timestamp):
                trade_date = raw_date.date()
            else:
                trade_date = raw_date

            record = {
                "symbol_code": symbol_code,
                "date": trade_date,
                "open": self._safe_float(row.get("开盘价")),
                "high": self._safe_float(row.get("最高价")),
                "low": self._safe_float(row.get("最低价")),
                "close": self._safe_float(row.get("收盘价")),
                "change_pct": self._safe_float(row.get("涨跌幅")),
                "change_amount": self._safe_float(row.get("涨跌额")),
                "amplitude": self._safe_float(row.get("振幅")),
            }
            records.append(record)

        return records

    def _safe_float(self, value) -> Optional[float]:
        """安全转换为float，处理NaN和None."""
        if value is None:
            return None
        try:
            import pandas as pd
            if pd.isna(value):
                return None
            return float(value)
        except (TypeError, ValueError):
            return None


# 全局采集器实例
akshare_collector = AKShareCollector()