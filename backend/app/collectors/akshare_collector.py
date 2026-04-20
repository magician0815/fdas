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
            # 在线程池中执行同步的AKShare调用
            df = await asyncio.to_thread(
                self._call_forex_hist,
                symbol_name,
                symbol_code,
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


# 全局采集器实例
akshare_collector = AKShareCollector()