"""
AKShare数据采集器.

使用AKShare库采集金融数据，支持forex_hist接口.

Author: FDAS Team
Created: 2026-04-03
Updated: 2026-04-10 - 适配ForexSymbol和ForexDaily模型
Updated: 2026-04-21 - 支持从配置文件加载参数
"""

from typing import List, Dict, Optional
from datetime import date
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
import asyncio

logger = logging.getLogger(__name__)


# 默认配置（当没有传入配置时使用）
DEFAULT_CONFIG = {
    "api": {
        "base_url": "https://push2his.eastmoney.com/api/qt/stock/kline/get",
        "method": "GET",
        "timeout": 30,
        "retry": {"max_attempt": 3, "backoff_factor": 2}
    },
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://quote.eastmoney.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    },
    "symbol_mapping": {
        "USDCNY": "133.USDCNH",
        "EURCNY": "133.EURCNH",
        "GBPCNY": "133.GBPCNH",
        "JPYCNY": "133.CNHJPY",
        "HKDCNY": "133.CNHHKD",
        "AUDCNY": "133.AUDCNH",
        "CADCNY": "133.CADCNH",
        "CHFCNY": "133.CHFCNH",
        "NZDCNY": "133.NZDCNH",
        "EURUSD": "133.EURUSD",
        "GBPUSD": "133.GBPUSD",
        "USDJPY": "133.USDJPY",
        "AUDUSD": "133.AUDUSD",
        "USDCAD": "133.USDCAD",
        "USDCHF": "133.USDCHF",
        "NZDUSD": "133.NZDUSD",
        "EURGBP": "133.EURGBP",
        "EURJPY": "133.EURJPY",
        "GBPJPY": "133.GBPJPY",
        "AUDJPY": "133.AUDJPY",
        "USDSGD": "133.USDSGD",
        "USDHKD": "133.USDHKD",
    },
    "data_parser": {
        "response_root": "data.klines",
        "date_field": 0,
        "open_field": 1,
        "high_field": 2,
        "low_field": 3,
        "close_field": 4,
        "volume_field": 5,
    }
}


class AKShareCollector:
    """
    AKShare数据采集器.

    使用AKShare库采集外汇数据，支持重试机制.
    支持从外部配置加载参数.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化采集器.

        Args:
            config: 配置字典，如果为None则使用默认配置
        """
        # 合并配置：默认配置 + 传入配置
        self.config = {**DEFAULT_CONFIG, **(config or {})}

        # 从配置中提取参数
        self._load_from_config()

    def _load_from_config(self):
        """从配置字典加载参数."""
        # API配置
        api_config = self.config.get("api", {})
        self.api_url = api_config.get("base_url", DEFAULT_CONFIG["api"]["base_url"])
        self.timeout = api_config.get("timeout", 30)
        self.retry_config = api_config.get("retry", {})

        # 请求头
        self.headers = {**DEFAULT_CONFIG["headers"], **self.config.get("headers", {})}

        # 货币对映射
        self.symbol_mapping = {**DEFAULT_CONFIG["symbol_mapping"], **self.config.get("symbol_mapping", {})}

        # 数据解析配置
        parser_config = self.config.get("data_parser", DEFAULT_CONFIG["data_parser"])
        self.date_field = parser_config.get("date_field", 0)
        self.open_field = parser_config.get("open_field", 1)
        self.high_field = parser_config.get("high_field", 2)
        self.low_field = parser_config.get("low_field", 3)
        self.close_field = parser_config.get("close_field", 4)
        self.volume_field = parser_config.get("volume_field", 5)

    async def fetch_supported_symbols(self) -> List[Dict]:
        """
        获取支持的货币对列表.

        从AKShare获取外汇货币对列表，返回中文名称和英文代码.

        Returns:
            List[Dict]: 货币对列表，格式为 [{"value": "美元人民币", "code": "USDCNY", "label": "美元人民币(USDCNY)"}]
        """
        logger.info("获取AKShare支持的货币对列表")

        try:
            # Python 3.11+ 使用 asyncio.to_thread，旧版本使用 run_in_executor
            if hasattr(asyncio, 'to_thread'):
                symbols = await asyncio.to_thread(
                    self._fetch_forex_symbols,
                )
            else:
                # Python 3.8-3.10 兼容
                loop = asyncio.get_event_loop()
                symbols = await loop.run_in_executor(None, self._fetch_forex_symbols)

            logger.info(f"获取到 {len(symbols)} 个货币对")
            return symbols

        except Exception as e:
            logger.error(f"获取货币对列表失败: {str(e)}")
            # 返回默认列表作为备用
            return self._get_default_symbols()

    def _fetch_forex_symbols(self) -> List[Dict]:
        """
        同步获取AKShare外汇货币对列表.

        从forex_em.symbol_market_map获取AKShare实际支持的货币对代码.

        Returns:
            List[Dict]: 货币对列表
        """
        try:
            import akshare.forex.forex_em as forex_em
        except ImportError:
            logger.warning("AKShare forex_em模块未找到，使用默认货币对列表")
            return self._get_default_symbols()

        try:
            # 从forex_em.symbol_market_map获取AKShare支持的货币对
            # 该映射表包含190个货币对代码和市场代码
            symbols = []

            # 市场代码说明：
            # 133 - 外汇离岸市场（主流交易）
            # 120 - 人民币中间价
            # 119 - 其他外汇市场
            for code, market_code in forex_em.symbol_market_map.items():
                # 生成中文名称（根据货币对代码）
                name = self._generate_symbol_name(code)

                symbols.append({
                    "value": name,      # 中文名称
                    "code": code,       # AKShare标准代码
                    "label": f"{name}({code})",
                    "market_code": market_code,
                })

            logger.info(f"从AKShare获取到 {len(symbols)} 个货币对")
            # 如果获取结果为空，使用默认列表
            if not symbols:
                logger.warning("AKShare返回空列表，使用默认货币对")
                return self._get_default_symbols()
            return symbols

        except Exception as e:
            logger.warning(f"获取forex_em.symbol_market_map失败: {str(e)}，使用默认列表")
            return self._get_default_symbols()

    def _generate_symbol_name(self, code: str) -> str:
        """
        根据货币对代码生成中文名称.

        Args:
            code: 货币对代码（如USDCNH、EURUSD）

        Returns:
            str: 中文名称（如"美元人民币"、"欧元美元")
        """
        # 货币代码映射表
        currency_names = {
            "USD": "美元",
            "EUR": "欧元",
            "GBP": "英镑",
            "JPY": "日元",
            "CNY": "人民币",
            "CNH": "离岸人民币",
            "CNYC": "人民币中间价",
            "AUD": "澳元",
            "NZD": "新西兰元",
            "CAD": "加元",
            "CHF": "瑞郎",
            "HKD": "港币",
            "SGD": "新加坡元",
            "ZAR": "南非兰特",
            "TRY": "土耳其里拉",
            "RUB": "俄罗斯卢布",
            "BRL": "巴西雷亚尔",
            "INR": "印度卢比",
            "KRW": "韩元",
            "MXN": "墨西哥比索",
            "NOK": "挪威克朗",
            "SEK": "瑞典克朗",
            "DKK": "丹麦克朗",
            "PLN": "波兰兹罗提",
            "THB": "泰铢",
            "IDR": "印尼盾",
            "MYR": "马来西亚林吉特",
            "PHP": "菲律宾比索",
            "VND": "越南盾",
        }

        # 特殊处理CNH/CNYC
        if code.endswith("CNH"):
            base = code[:3]
            return f"{currency_names.get(base, base)}离岸人民币"
        elif code.endswith("CNYC"):
            base = code[:3]
            return f"{currency_names.get(base, base)}人民币中间价"
        elif code.endswith("CNY"):
            base = code[:3]
            return f"{currency_names.get(base, base)}人民币"
        elif code.startswith("CNY") or code.startswith("CNH"):
            # 反向货币对（如CNHUSD）
            quote = code[3:]
            base = code[:3]
            return f"{currency_names.get(base, base)}{currency_names.get(quote, quote)}"
        else:
            # 标准货币对（如EURUSD）
            base = code[:3]
            quote = code[3:]
            return f"{currency_names.get(base, base)}{currency_names.get(quote, quote)}"

    def _get_default_symbols(self) -> List[Dict]:
        """
        返回默认货币对列表.

        当AKShare接口无法获取时使用此列表.
        使用AKShare标准代码（离岸人民币CNH）。

        Returns:
            List[Dict]: 默认货币对列表
        """
        # 使用AKShare标准代码（市场代码133=离岸外汇）
        default_symbols = [
            {"value": "美元离岸人民币", "code": "USDCNH", "label": "美元离岸人民币(USDCNH)"},
            {"value": "欧元美元", "code": "EURUSD", "label": "欧元美元(EURUSD)"},
            {"value": "英镑美元", "code": "GBPUSD", "label": "英镑美元(GBPUSD)"},
            {"value": "美元日元", "code": "USDJPY", "label": "美元日元(USDJPY)"},
            {"value": "美元港币", "code": "USDHKD", "label": "美元港币(USDHKD)"},
            {"value": "美元瑞郎", "code": "USDCHF", "label": "美元瑞郎(USDCHF)"},
            {"value": "澳元美元", "code": "AUDUSD", "label": "澳元美元(AUDUSD)"},
            {"value": "新西兰元美元", "code": "NZDUSD", "label": "新西兰元美元(NZDUSD)"},
            {"value": "美元加元", "code": "USDCAD", "label": "美元加元(USDCAD)"},
            {"value": "美元新加坡元", "code": "USDSGD", "label": "美元新加坡元(USDSGD)"},
            {"value": "欧元离岸人民币", "code": "EURCNH", "label": "欧元离岸人民币(EURCNH)"},
            {"value": "英镑离岸人民币", "code": "GBPCNH", "label": "英镑离岸人民币(GBPCNH)"},
            {"value": "离岸人民币日元", "code": "CNHJPY", "label": "离岸人民币日元(CNHJPY)"},
            {"value": "离岸人民币港币", "code": "CNHHKD", "label": "离岸人民币港币(CNHHKD)"},
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
            # Python 3.11+ 使用 asyncio.to_thread，旧版本使用 run_in_executor
            if hasattr(asyncio, 'to_thread'):
                df = await asyncio.to_thread(
                    self._call_forex_hist,
                    symbol_name,
                    symbol_code,
                    start_date,
                    end_date,
                )
            else:
                # Python 3.8-3.10 兼容
                loop = asyncio.get_event_loop()
                df = await loop.run_in_executor(
                    None, self._call_forex_hist, symbol_name, symbol_code, start_date, end_date
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
        symbol_code: str,
        start_date: date,
        end_date: date,
    ):
        """
        直接调用东方财富API获取外汇历史数据.

        由于AKShare库的forex_hist_em接口内部未添加必要的请求头，
        导致API拒绝连接。此方法直接调用东方财富API并添加必要的User-Agent和Referer头。

        Args:
            symbol_name: 货币对名称（中文）
            symbol_code: 货币对代码（英文，如USDCNY）
            start_date: 开始日期（用于数据筛选）
            end_date: 结束日期（用于数据筛选）

        Returns:
            DataFrame: API返回的数据
        """
        import requests
        import pandas as pd

        # 使用配置中的API地址
        api_url = self.api_url

        # 使用配置中的请求头
        headers = self.headers

        # 使用配置中的货币对映射
        symbol_mapping = self.symbol_mapping

        # 获取secid
        secid = symbol_mapping.get(symbol_code, symbol_mapping.get(symbol_name))

        if not secid:
            # 尝试直接构造：默认使用市场代码133
            logger.warning(f"货币对 {symbol_code}/{symbol_name} 未在映射表中，使用默认市场代码133")
            secid = f"133.{symbol_code}"

        logger.debug(f"API调用: secid={secid} (原始: {symbol_code}/{symbol_name})")

        # 构造请求参数
        # fields: kline数据字段
        # klt: 101=日K线, 102=周K线, 103=月K线
        # fqt: 0=不复权, 1=前复权, 2=后复权
        # beg/end: 日期范围
        params = {
            'secid': secid,
            'fields1': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62',
            'klt': '101',  # 日K线
            'fqt': '0',    # 不复权
            'beg': start_date.strftime('%Y%m%d'),
            'end': end_date.strftime('%Y%m%d'),
            'ut': 'b2884a393a59ad6400a92d7a8234642',  # 固定token
        }

        try:
            response = requests.get(api_url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if data.get('rc') != 0 or not data.get('data'):
                logger.warning(f"API返回无数据: {data}")
                return pd.DataFrame()

            klines = data.get('data', {}).get('klines', [])
            if not klines:
                logger.warning(f"API返回klines为空")
                return pd.DataFrame()

            # 解析klines数据
            # 格式: 日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
            records = []
            for line in klines:
                parts = line.split(',')
                if len(parts) >= 10:
                    records.append({
                        '日期': parts[0],
                        '今开': parts[1],
                        '最新价': parts[2],
                        '最高': parts[3],
                        '最低': parts[4],
                        '涨跌幅': parts[8],
                        '涨跌额': parts[9],
                        '振幅': parts[7] if len(parts) > 7 else None,
                    })

            df = pd.DataFrame(records)
            logger.info(f"成功获取 {len(df)} 条历史数据")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"数据解析失败: {str(e)}")
            raise

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

        # AKShare forex_hist_em返回字段：
        # 日期, 代码, 名称, 今开, 最新价, 最高, 最低, 振幅
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

            # 字段映射：今开->open, 最新价->close, 最高->high, 最低->low
            # 注意：不包含symbol_code，该字段在forex_daily_service中由symbol_id替代
            record = {
                "date": trade_date,
                "open": self._safe_float(row.get("今开")),
                "high": self._safe_float(row.get("最高")),
                "low": self._safe_float(row.get("最低")),
                "close": self._safe_float(row.get("最新价")),
                "volume": 0,  # 外汇数据通常无成交量
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

    async def collect_stock_a_daily(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
        adjust: str = "",
    ) -> List[Dict]:
        """
        采集A股日线行情数据。

        调用AKShare stock_zh_a_daily接口获取历史数据。

        Args:
            symbol_name: 股票名称（中文如"贵州茅台"）
            symbol_code: 股票代码（sh600519或sz000001）
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型 (""=不复权, "qfq"=前复权, "hfq"=后复权)

        Returns:
            List[Dict]: 股票行情数据列表
        """
        logger.info(f"开始采集A股数据: {symbol_name} ({symbol_code}), {start_date} ~ {end_date}, adjust={adjust}")

        try:
            # Python 3.11+ 使用 asyncio.to_thread，旧版本使用 run_in_executor
            if hasattr(asyncio, 'to_thread'):
                df = await asyncio.to_thread(
                    self._call_stock_a_daily,
                    symbol_code,
                    start_date,
                    end_date,
                    adjust,
                )
            else:
                # Python 3.8-3.10 兼容
                loop = asyncio.get_event_loop()
                df = await loop.run_in_executor(
                    None, self._call_stock_a_daily, symbol_code, start_date, end_date, adjust
                )

            if df is None or df.empty:
                logger.warning(f"采集A股数据为空: {symbol_name}")
                return []

            records = self._transform_stock_data(df, symbol_code)

            logger.info(f"成功采集 {len(records)} 条 {symbol_name} 数据")
            return records

        except Exception as e:
            logger.error(f"采集A股数据失败: {str(e)}")
            raise

    def _call_stock_a_daily(
        self,
        symbol_code: str,
        start_date: date,
        end_date: date,
        adjust: str = "",
    ):
        """
        调用AKShare stock_zh_a_daily接口获取A股数据。

        Args:
            symbol_code: 股票代码（sh600519, sz000001等）
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型 (""=不复权, "qfq"=前复权, "hfq"=后复权)

        Returns:
            DataFrame: API返回的数据
        """
        import akshare as ak
        import pandas as pd

        # 调用AKShare接口（使用stock_zh_a_hist支持复权）
        df = ak.stock_zh_a_hist(
            symbol=symbol_code,
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            adjust=adjust,
        )

        if df is None or df.empty:
            return df

        # 按日期排序
        df = df.sort_values("date")

        return df

    def _transform_stock_data(self, df, symbol_code: str, market_code: str = "stock_cn") -> List[Dict]:
        """
        转换股票数据格式为数据库存储格式。

        Args:
            df: pandas DataFrame
            symbol_code: 股票代码
            market_code: 市场代码 (stock_cn/stock_us/stock_hk)

        Returns:
            List[Dict]: 转换后的数据列表
        """
        import pandas as pd

        records = []
        for _, row in df.iterrows():
            # 字段映射修正：
            # - turnover (换手率) → turnover
            # - pct_chg (涨跌幅) → change_pct
            # - vol (成交量) → volume
            # - amount (成交额) → amount
            record = {
                "date": pd.to_datetime(row["date"]).strftime("%Y-%m-%d"),
                "open": self._safe_float(row.get("open")),
                "high": self._safe_float(row.get("high")),
                "low": self._safe_float(row.get("low")),
                "close": self._safe_float(row.get("close")),
                "volume": int(self._safe_float(row.get("volume", 0)) or 0),
                "amount": self._safe_float(row.get("amount")),
                "turnover": self._safe_float(row.get("turnover")),  # 换手率
                "change_pct": self._safe_float(row.get("pct_chg")),  # 涨跌幅
                "change_amount": self._safe_float(row.get("change")) or self._safe_float(row.get("pct_chg")),
                "amplitude": self._safe_float(row.get("amplitude")),
            }
            records.append(record)

        return records

    async def collect_daily(
        self,
        config: Dict,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        统一采集入口方法.

        根据配置中的collector_type分派到对应采集方法.

        Args:
            config: 数据源配置字典
            symbol: 标的代码/名称
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            List[Dict]: 采集的数据列表
        """
        collector_type = config.get("collector_type", "akshare_native")

        if collector_type == "http_api":
            # TODO: 实现HTTP API采集（后续阶段）
            raise NotImplementedError("HTTP API采集器尚未实现")
        elif collector_type == "akshare_native":
            return await self._collect_by_akshare_interface(config, symbol, start_date, end_date)
        else:
            raise ValueError(f"不支持的采集器类型: {collector_type}")

    async def _collect_by_akshare_interface(
        self,
        config: Dict,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        根据AKShare接口名分派采集.

        Args:
            config: 数据源配置字典
            symbol: 标的代码/名称
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            List[Dict]: 采集的数据列表
        """
        interface = config.get("akshare_interface", "")
        market = config.get("market", "")

        # 接口分派映射
        dispatch_map = {
            "forex_hist": self.collect_forex_hist,
            "stock_zh_a_hist": self.collect_stock_a_daily,
            "stock_us_daily": self.collect_stock_us_daily,
            "stock_hk_daily": self.collect_stock_hk_daily,
            "futures_zh_daily_sina": self.collect_futures_daily,
            "bond_cn_daily": self.collect_bond_daily,
            "bond_us_daily": self.collect_bond_us_daily,
        }

        collector_method = dispatch_map.get(interface)
        if not collector_method:
            raise ValueError(f"不支持的AKShare接口: {interface}")

        # 调用对应采集方法
        if interface == "forex_hist":
            return await collector_method(symbol, symbol, start_date, end_date)
        else:
            return await collector_method(symbol, symbol, start_date, end_date)

    async def fetch_symbols_by_config(self, config: Dict) -> List[Dict]:
        """
        基于配置获取标的列表.

        Args:
            config: 数据源配置字典

        Returns:
            List[Dict]: 标的列表
        """
        symbol_fetch = config.get("symbol_fetch")
        if not symbol_fetch:
            # 无标的获取配置，返回空列表
            logger.warning("配置中未提供symbol_fetch，无法获取标的列表")
            return []

        interface = symbol_fetch.get("interface")
        if not interface:
            raise ValueError("symbol_fetch.interface 未配置")

        # 分派到对应接口的标的获取方法
        if interface == "stock_zh_a_spot_em":
            return await self._fetch_stock_cn_symbols()
        elif interface == "stock_us_spot_em":
            return await self._fetch_stock_us_symbols()
        elif interface == "stock_hk_spot_em":
            return await self._fetch_stock_hk_symbols()
        elif interface == "futures_zh_spot_em":
            return await self._fetch_futures_symbols()
        elif interface == "bond_zh_spot_em":
            return await self._fetch_bond_cn_symbols()
        elif interface == "bond_gb_us_sina":
            return await self._fetch_bond_us_symbols()
        else:
            logger.warning(f"不支持的标的获取接口: {interface}")
            return []

    # ========== 新市场骨架方法 ==========

    async def collect_stock_us_daily(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        采集美股日线行情数据（骨架）.
        """
        logger.info(f"开始采集美股数据: {symbol_name} ({symbol_code}), {start_date} ~ {end_date}")
        return await self._call_stock_market_daily("us", symbol_code, start_date, end_date)

    async def collect_stock_hk_daily(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        采集港股日线行情数据（骨架）.
        """
        logger.info(f"开始采集港股数据: {symbol_name} ({symbol_code}), {start_date} ~ {end_date}")
        return await self._call_stock_market_daily("hk", symbol_code, start_date, end_date)

    async def _call_stock_market_daily(
        self,
        market: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        调用AKShare股票接口的统一方法.

        Args:
            market: 市场标识 (us/hk)
            symbol_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            List[Dict]: 股票行情数据
        """
        import akshare as ak
        import pandas as pd

        try:
            if market == "us":
                # 美股：东方财富美股历史数据
                # symbol_code 格式: 105.MSFT (需要从spot接口获取实际代码)
                df = await asyncio.to_thread(
                    ak.stock_us_hist,
                    symbol=symbol_code,
                    start_date=start_date.strftime("%Y%m%d"),
                    end_date=end_date.strftime("%Y%m%d"),
                    adjust="",
                )
            elif market == "hk":
                # 港股：东方财富港股��史数据
                df = await asyncio.to_thread(
                    ak.stock_hk_daily,
                    symbol=symbol_code,
                    start_date=start_date.strftime("%Y%m%d"),
                    end_date=end_date.strftime("%Y%m%d"),
                )
            else:
                raise ValueError(f"不支持的股票市场: {market}")

            if df is None or df.empty:
                return []

            # 过滤日期范围
            df["date"] = pd.to_datetime(df["date"])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)]

            # 转换格式
            records = []
            for _, row in df.iterrows():
                record = {
                    "date": pd.to_datetime(row["date"]).strftime("%Y-%m-%d"),
                    "open": self._safe_float(row.get("open")),
                    "high": self._safe_float(row.get("high")),
                    "low": self._safe_float(row.get("low")),
                    "close": self._safe_float(row.get("close")),
                    "volume": int(self._safe_float(row.get("volume", 0)) or 0),
                    "amount": self._safe_float(row.get("amount")),
                    "change_pct": self._safe_float(row.get("pct_chg")),
                    "change_amount": self._safe_float(row.get("change")),
                    "amplitude": self._safe_float(row.get("amplitude")),
                }
                records.append(record)

            return records

        except Exception as e:
            logger.error(f"获取股票数据失败: {str(e)}")
            raise

    async def collect_bond_daily(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        采集国内债券日线行情数据（骨架）.
        """
        logger.info(f"开始采集国内债券数据: {symbol_name} ({symbol_code}), {start_date} ~ {end_date}")
        return await self._call_bond_daily("cn", symbol_code, start_date, end_date)

    async def collect_bond_us_daily(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        采集美国债券日线行情数据（骨架）.
        """
        logger.info(f"开始采集美国债券数据: {symbol_name} ({symbol_code}), {start_date} ~ {end_date}")
        return await self._call_bond_daily("us", symbol_code, start_date, end_date)

    async def _call_bond_daily(
        self,
        market: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        调用AKShare债券接口的统一方法.

        Args:
            market: 市场标识 (cn/us)
            symbol_code: 债券代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            List[Dict]: 债券行情数据
        """
        import akshare as ak
        import pandas as pd

        try:
            if market == "cn":
                # 国内债券：新浪财经沪深债券
                # symbol_code 格式: sh010107 或 sz123456
                df = await asyncio.to_thread(ak.bond_zh_hs_daily, symbol=symbol_code)
            elif market == "us":
                # 美国国债：新浪财经美国国债收益率
                # symbol_code 支持: 美国1年期国债, 美国2年期国债...美国30年期国债
                # 默认为10年期
                symbol = symbol_code if symbol_code else "美国10年期国债"
                df = await asyncio.to_thread(ak.bond_gb_us_sina, symbol=symbol)
            else:
                raise ValueError(f"不支持的债券市场: {market}")

            if df is None or df.empty:
                return []

            # 过滤日期范围
            df["date"] = pd.to_datetime(df["date"])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)]

            # 转换格式
            records = []
            for _, row in df.iterrows():
                record = {
                    "date": pd.to_datetime(row["date"]).strftime("%Y-%m-%d"),
                    "open": self._safe_float(row.get("open")),
                    "high": self._safe_float(row.get("high")),
                    "low": self._safe_float(row.get("low")),
                    "close": self._safe_float(row.get("close")),
                    "yield_rate": self._safe_float(row.get("yield")),
                    "volume": int(self._safe_float(row.get("volume", 0)) or 0),
                    "amount": self._safe_float(row.get("amount")),
                    "change_pct": self._safe_float(row.get("pct_chg")),
                    "change_amount": self._safe_float(row.get("change")),
                    "amplitude": self._safe_float(row.get("amplitude")),
                }
                records.append(record)

            return records

        except Exception as e:
            logger.error(f"获取债券数据失败: {str(e)}")
            raise

    async def collect_futures_daily(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        采集期货日线行情数据。

        调用AKShare futures_zh_daily_sina接口获取历史数据。

        Args:
            symbol_name: 期货品种名称（如"螺纹钢"）
            symbol_code: 期货合约代码（如"RB2105"）
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            List[Dict]: 期货行情数据列表
        """
        logger.info(f"开始采集期货数据: {symbol_name} ({symbol_code}), {start_date} ~ {end_date}")

        try:
            # Python 3.11+ 使用 asyncio.to_thread
            if hasattr(asyncio, 'to_thread'):
                df = await asyncio.to_thread(
                    self._call_futures_daily,
                    symbol_code,
                    start_date,
                    end_date,
                )
            else:
                loop = asyncio.get_event_loop()
                df = await loop.run_in_executor(
                    None, self._call_futures_daily, symbol_code, start_date, end_date
                )

            if df is None or df.empty:
                logger.warning(f"采集期货数据为空: {symbol_name}")
                return []

            records = self._transform_futures_data(df, symbol_code)

            logger.info(f"成功采集 {len(records)} 条 {symbol_name} 数据")
            return records

        except Exception as e:
            logger.error(f"采集期货数据失败: {str(e)}")
            raise

    def _call_futures_daily(
        self,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ):
        """调用AKShare futures_zh_daily_sina接口获取期货数据."""
        import akshare as ak
        import pandas as pd

        # 调用AKShare接口
        df = ak.futures_zh_daily_sina(symbol=symbol_code)

        # 过滤日期范围
        df["date"] = pd.to_datetime(df["date"])
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)]

        # 按日期排序
        df = df.sort_values("date")

        return df

    def _transform_futures_data(self, df, symbol_code: str) -> List[Dict]:
        """转换期货数据格式为数据库存储格式."""
        import pandas as pd

        records = []
        for _, row in df.iterrows():
            record = {
                "date": pd.to_datetime(row["date"]).strftime("%Y-%m-%d"),
                "open": self._safe_float(row.get("open")),
                "high": self._safe_float(row.get("high")),
                "low": self._safe_float(row.get("low")),
                "close": self._safe_float(row.get("close")),
                "volume": int(self._safe_float(row.get("volume", 0)) or 0),
                "amount": self._safe_float(row.get("amount")),
                "change_pct": self._safe_float(row.get("pct_chg")),
                "change_amount": self._safe_float(row.get("change")),
                "amplitude": self._safe_float(row.get("amplitude")),
            }
            records.append(record)

        return records

    # ========== 标的获取方法 ==========

    async def _fetch_stock_cn_symbols(self) -> List[Dict]:
        """获取A股标的列表."""
        try:
            import akshare as ak
            import pandas as pd

            # 调用AKShare接口获取A股实时行情
            df = await asyncio.to_thread(ak.stock_zh_a_spot_em)

            # 转换为统一格式
            records = []
            for _, row in df.iterrows():
                # 判断交易所：上证以sh开头，深证以sz开头，北交所以bj开头
                code = str(row.get("代码", ""))
                if code.startswith("6"):
                    exchange = "sh"
                elif code.startswith("0") or code.startswith("3"):
                    exchange = "sz"
                elif code.startswith("8") or code.startswith("4"):
                    exchange = "bj"
                else:
                    exchange = "sz"

                records.append({
                    "code": code,
                    "name": row.get("名称", ""),
                    "exchange": exchange,
                    "market_code": "stock_cn",
                })

            logger.info(f"获取A股标的列表成功，共 {len(records)} 条")
            return records

        except Exception as e:
            logger.error(f"获取A股标的列表失败: {str(e)}")
            raise

    async def _fetch_stock_us_symbols(self) -> List[Dict]:
        """获取美股标的列表（骨架）."""
        raise NotImplementedError("美股标的获取接口尚未实现")

    async def _fetch_stock_hk_symbols(self) -> List[Dict]:
        """获取港股标的列表（骨架）."""
        raise NotImplementedError("港股标的获取接口尚未实现")

    async def _fetch_futures_symbols(self) -> List[Dict]:
        """获取国内期货标的列表."""
        try:
            import akshare as ak
            import pandas as pd

            # 采集各交易所的期货合约信息
            all_contracts = []

            # 中金所 (CFFEX)
            try:
                df_cffex = await asyncio.to_thread(ak.futures_contract_info_cffex)
                for _, row in df_cffex.iterrows():
                    all_contracts.append({
                        "code": str(row.get("合约代码", "")),
                        "name": str(row.get("品种", "")),
                        "exchange": "cffex",
                        "variety": str(row.get("品种", "")),
                        "market_code": "futures_cn",
                    })
            except Exception as e:
                logger.warning(f"获取中金所合约信息失败: {e}")

            # 大商所 (DCE)
            try:
                df_dce = await asyncio.to_thread(ak.futures_contract_info_dce)
                for _, row in df_dce.iterrows():
                    all_contracts.append({
                        "code": str(row.get("合约代码", "")),
                        "name": str(row.get("品种", "")),
                        "exchange": "dce",
                        "variety": str(row.get("品种", "")),
                        "market_code": "futures_cn",
                    })
            except Exception as e:
                logger.warning(f"获取大商所合约信息失败: {e}")

            # 郑商所 (CZCE)
            try:
                df_czce = await asyncio.to_thread(ak.futures_contract_info_czce)
                for _, row in df_czce.iterrows():
                    all_contracts.append({
                        "code": str(row.get("合约代码", "")),
                        "name": str(row.get("品种", "")),
                        "exchange": "czce",
                        "variety": str(row.get("品种", "")),
                        "market_code": "futures_cn",
                    })
            except Exception as e:
                logger.warning(f"获取郑商所合约信息失败: {e}")

            # 上期所 (SHFE)
            try:
                df_shfe = await asyncio.to_thread(ak.futures_contract_info_shfe)
                for _, row in df_shfe.iterrows():
                    all_contracts.append({
                        "code": str(row.get("合约代码", "")),
                        "name": str(row.get("品种", "")),
                        "exchange": "shfe",
                        "variety": str(row.get("品种", "")),
                        "market_code": "futures_cn",
                    })
            except Exception as e:
                logger.warning(f"获取上期所合约信息失败: {e}")

            # 去重
            seen = set()
            unique_contracts = []
            for c in all_contracts:
                if c["code"] not in seen:
                    seen.add(c["code"])
                    unique_contracts.append(c)

            logger.info(f"获取期货标的列表成功，共 {len(unique_contracts)} 条")
            return unique_contracts

        except Exception as e:
            logger.error(f"获取期货标的列表失败: {str(e)}")
            raise

    async def _fetch_bond_cn_symbols(self) -> List[Dict]:
        """获取国内债券标的列表（骨架）."""
        raise NotImplementedError("国内债券标的获取接口尚未实现")

    async def _fetch_bond_us_symbols(self) -> List[Dict]:
        """获取美债标的列表（美国国债收益率曲线）."""
        # 美国国债是固定期限品种，不是从API动态获取
        us_bond_symbols = [
            {"code": "美国1月期国债", "name": "美国1月期国债", "market_code": "bond_us"},
            {"code": "美国2月期国债", "name": "美国2月期国债", "market_code": "bond_us"},
            {"code": "美国3月期国债", "name": "美国3月期国债", "market_code": "bond_us"},
            {"code": "美国4月期国债", "name": "美国4月期国债", "market_code": "bond_us"},
            {"code": "美国6月期国债", "name": "美国6月期国债", "market_code": "bond_us"},
            {"code": "美国1年期国债", "name": "美国1年期国债", "market_code": "bond_us"},
            {"code": "美国2年期国债", "name": "美国2年期国债", "market_code": "bond_us"},
            {"code": "美国3年期国债", "name": "美国3年期国债", "market_code": "bond_us"},
            {"code": "美国5年期国债", "name": "美国5年期国债", "market_code": "bond_us"},
            {"code": "美国7年期国债", "name": "美国7年期国债", "market_code": "bond_us"},
            {"code": "美国10年期国债", "name": "美国10年期国债", "market_code": "bond_us"},
            {"code": "美国20年期国债", "name": "美国20年期国债", "market_code": "bond_us"},
            {"code": "美国30年期国债", "name": "美国30年期国债", "market_code": "bond_us"},
        ]
        logger.info(f"获取美债标的列表成功，共 {len(us_bond_symbols)} 条")
        return us_bond_symbols


# 全局采集器实例
akshare_collector = AKShareCollector()