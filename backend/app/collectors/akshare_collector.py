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
        采集外汇日线行情数据（主源东方财富 + 备源中国银行牌价）.
        """
        logger.info(f"开始采集外汇数据: {symbol_name} ({symbol_code}), {start_date} ~ {end_date}")

        # 主源：东方财富HTTP API
        try:
            df = await asyncio.to_thread(self._call_forex_hist, symbol_name, symbol_code, start_date, end_date)
            if df is not None and not df.empty:
                records = self._transform_data(df, symbol_code)
                logger.info(f"东方财富源成功采集 {len(records)} 条 {symbol_name} 数据")
                return records
            logger.warning(f"东方财富源返回空数据: {symbol_name}")
        except Exception as e:
            logger.warning(f"东方财富源采集失败: {symbol_name}, {str(e)[:100]}")

        # 备源：中国银行牌价 (currency_boc_sina)
        try:
            logger.info(f"回退到中国银行牌价源: {symbol_name} ({symbol_code})")
            df_boc = await asyncio.to_thread(self._call_forex_boc, symbol_name, symbol_code, start_date, end_date)
            if df_boc is not None and not df_boc.empty:
                records = self._transform_forex_boc_data(df_boc, symbol_code)
                logger.info(f"中国银行牌价源成功采集 {len(records)} 条 {symbol_name} 数据")
                return records
            logger.warning(f"中国银行牌价源返回空数据: {symbol_name}")
        except Exception as e2:
            logger.error(f"中国银行牌价源采集也失败: {symbol_name}, {str(e2)[:100]}")

        raise Exception(f"所有外汇数据源均无法采集 {symbol_name}: 东方财富和中国银行牌价均失败")

    def _call_forex_boc(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ):
        """
        调用中国银行牌价API (currency_boc_sina) 获取外汇参考汇率.

        作为东方财富源的备选，提供央行中间价数据（非OHLC格式）.

        Args:
            symbol_name: 货币对名称（中文，如"美元人民币"）
            symbol_code: 货币对代码
            start_date: 开始日期（用于筛选）
            end_date: 结束日期（用于筛选）

        Returns:
            DataFrame: 含OHLC格式的汇率数据
        """
        import akshare as ak
        import pandas as pd

        # 从货币对名称提取基准货币中文名（如"美元离岸人民币" → "美元"）
        currency_map = {
            "USD": "美元", "EUR": "欧元", "JPY": "日元", "GBP": "英镑",
            "HKD": "港币", "AUD": "澳大利亚元", "CAD": "加拿大元",
            "CHF": "瑞士法郎", "NZD": "新西兰元", "SGD": "新加坡元",
            "KRW": "韩国元", "MOP": "澳门元", "MYR": "马来西亚林吉特",
            "RUB": "俄罗斯卢布", "ZAR": "南非兰特", "THB": "泰国铢",
            "CNY": "人民币", "CNH": "人民币",
        }
        base = symbol_code[:3]
        boc_name = currency_map.get(base)
        if not boc_name:
            # 回退：在中文名称中匹配已知货币名
            for name in currency_map.values():
                if name in symbol_name:
                    boc_name = name
                    break
            if not boc_name:
                boc_name = "美元"  # 最终降级

        df = ak.currency_boc_sina(symbol=boc_name)

        if df is None or df.empty:
            return pd.DataFrame()

        # BOC column mapping: 日期→date, 央行中间价→close/open/high/low
        df = df.rename(columns={"日期": "date", "央行中间价": "close"})
        df["open"] = df["close"]
        df["high"] = df["close"]
        df["low"] = df["close"]
        df["volume"] = 0
        df["amount"] = 0.0

        # Filter by date range
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
        df = df.sort_values("date")

        if len(df) >= 2:
            df["change_pct"] = df["close"].pct_change() * 100
            df["change_amount"] = df["close"].diff()

        cols = ["date", "open", "high", "low", "close", "volume", "amount"]
        for c in ["change_pct", "change_amount"]:
            if c in df.columns:
                cols.append(c)
        return df[cols]

    def _transform_forex_boc_data(self, df, symbol_code: str) -> List[Dict]:
        """
        转换中国银行牌价数据为统一格式.
        """
        records = []
        for _, row in df.iterrows():
            date_val = row["date"]
            if hasattr(date_val, 'strftime'):
                date_str = date_val.strftime("%Y-%m-%d")
            else:
                date_str = str(date_val)[:10]
            records.append({
                "date": date_str,
                "code": symbol_code,
                "open": self._safe_float(row.get("open")),
                "high": self._safe_float(row.get("high")),
                "low": self._safe_float(row.get("low")),
                "close": self._safe_float(row.get("close")),
                "volume": int(self._safe_float(row.get("volume", 0)) or 0),
                "change_pct": self._safe_float(row.get("change_pct") if "change_pct" in row.index else None),
                "change_amount": self._safe_float(row.get("change_amount") if "change_amount" in row.index else None),
                "amplitude": 0,
            })
        return records

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
        采集A股日线行情数据（主源新浪 + 备源腾讯自动回退）.

        Args:
            symbol_name: 股票名称
            symbol_code: 股票代码（sh600519或sz000001）
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型

        Returns:
            List[Dict]: 股票行情数据列表
        """
        logger.info(f"开始采集A股数据: {symbol_name} ({symbol_code}), {start_date} ~ {end_date}, adjust={adjust}")

        # 主源：新浪 stock_zh_a_daily
        try:
            df = await asyncio.to_thread(self._call_stock_a_daily, symbol_code, start_date, end_date, adjust)
            if df is not None and not df.empty:
                records = self._transform_stock_data(df, symbol_code)
                logger.info(f"新浪源成功采集 {len(records)} 条 {symbol_name} 数据")
                return records
            logger.warning(f"新浪源返回空数据: {symbol_name}")
        except Exception as e:
            logger.warning(f"新浪源采集失败: {symbol_name}, {str(e)[:100]}")

        # 备源：腾讯 stock_zh_a_hist_tx
        try:
            logger.info(f"回退到腾讯源: {symbol_name} ({symbol_code})")
            df_tx = await asyncio.to_thread(self._call_stock_a_daily_tx, symbol_code, start_date, end_date, adjust)
            if df_tx is not None and not df_tx.empty:
                # 腾讯源无volume字段，补充默认值
                if "volume" not in df_tx.columns:
                    df_tx["volume"] = 0
                # 腾讯源无amount列名差异，统一处理
                if "amount" in df_tx.columns and "turnover" not in df_tx.columns:
                    pass  # amount already present
                records = self._transform_stock_data(df_tx, symbol_code)
                logger.info(f"腾讯源成功采集 {len(records)} 条 {symbol_name} 数据")
                return records
            logger.warning(f"腾讯源返回空数据: {symbol_name}")
        except Exception as e2:
            logger.error(f"腾讯源采集也失败: {symbol_name}, {str(e2)[:100]}")

        # 两个源都失败
        raise Exception(f"所有数据源均无法采集 {symbol_name}: 新浪和腾讯源均失败")

    def _call_stock_a_daily(
        self,
        symbol_code: str,
        start_date: date,
        end_date: date,
        adjust: str = "",
    ):
        """
        调用AKShare stock_zh_a_daily (新浪源) 获取A股数据.

        注意: stock_zh_a_hist (东方财富源) 易被屏蔽连接, 改用新浪源.

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

        df = ak.stock_zh_a_daily(
            symbol=symbol_code,
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            adjust=adjust,
        )

        if df is None or df.empty:
            return df

        # 按日期排序
        df = df.sort_values("date")

        # 计算涨跌幅和振幅 (新浪源不直接提供)
        if "change_pct" not in df.columns and len(df) >= 2:
            df["change_pct"] = df["close"].pct_change() * 100
        if "change_amount" not in df.columns and len(df) >= 2:
            df["change_amount"] = df["close"].diff()
        if "amplitude" not in df.columns:
            df["amplitude"] = (df["high"] - df["low"]) / df["close"].shift(1) * 100

        return df

    def _call_stock_a_daily_tx(
        self,
        symbol_code: str,
        start_date: date,
        end_date: date,
        adjust: str = "",
    ):
        """
        调用AKShare stock_zh_a_hist_tx (腾讯源) 获取A股数据.

        作为新浪源的备选，腾讯源稳定但缺少volume字段.
        支持复权参数 qfq/hfq.

        Args:
            symbol_code: 带交易所前缀的代码 (sh600519, sz000001)
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型

        Returns:
            DataFrame: API返回的数据
        """
        import akshare as ak
        import pandas as pd

        df = ak.stock_zh_a_hist_tx(
            symbol=symbol_code,
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            adjust=adjust,
        )

        if df is None or df.empty:
            return df

        df = df.sort_values("date")

        # 腾讯源字段: date, open, close, high, low, amount (无volume)
        if "volume" not in df.columns:
            df["volume"] = 0
        # 计算涨跌幅和振幅
        if "change_pct" not in df.columns and len(df) >= 2:
            df["change_pct"] = df["close"].pct_change() * 100
        if "change_amount" not in df.columns and len(df) >= 2:
            df["change_amount"] = df["close"].diff()
        if "amplitude" not in df.columns:
            df["amplitude"] = (df["high"] - df["low"]) / df["close"].shift(1) * 100

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
            record = {
                "date": pd.to_datetime(row["date"]).strftime("%Y-%m-%d"),
                "open": self._safe_float(row.get("open")),
                "high": self._safe_float(row.get("high")),
                "low": self._safe_float(row.get("low")),
                "close": self._safe_float(row.get("close")),
                "volume": int(self._safe_float(row.get("volume", 0)) or 0),
                "amount": self._safe_float(row.get("amount")),
                "turnover": self._safe_float(row.get("turnover")),
                # 兼容 sina 源 (change_pct/change_amount/amplitude 在 _call 中计算) 和 eastmoney 源 (pct_chg/change)
                "change_pct": self._safe_float(row.get("change_pct") or row.get("pct_chg")),
                "change_amount": self._safe_float(row.get("change_amount") or row.get("change")),
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
            return await self._collect_by_http_api(config, symbol, start_date, end_date)
        elif collector_type == "akshare_native":
            return await self._collect_by_akshare_interface(config, symbol, start_date, end_date)
        else:
            raise ValueError(f"不支持的采集器类型: {collector_type}")

    async def _collect_by_http_api(
        self,
        config: Dict,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        通过HTTP API采集数据.

        支持JSON响应和CSV响应两种格式.
        使用配置中的api、data_parser、symbol_mapping字段.

        Args:
            config: 数据源配置字典
            symbol: 标的代码/名称
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            List[Dict]: 统一格式的数据记录列表
        """
        import requests

        api_config = config.get("api", {})
        base_url = api_config.get("base_url", "")
        method = api_config.get("method", "GET").upper()
        timeout = api_config.get("timeout", 30)
        retry_cfg = api_config.get("retry", {"max_attempt": 3, "backoff_factor": 2})

        headers = config.get("headers", {})
        params = dict(config.get("params", {}))
        symbol_mapping = config.get("symbol_mapping", {})
        parser_cfg = config.get("data_parser", {})

        # 应用标的映射（config 优先，回退到 AKShare 自身的 symbol_market_map）
        api_symbol = symbol_mapping.get(symbol)
        if api_symbol is None:
            try:
                from akshare.forex import forex_em
                api_symbol = forex_em.symbol_market_map.get(symbol, symbol)
            except ImportError:
                api_symbol = symbol

        # 注入请求参数中的动态值
        for key, val in params.items():
            if isinstance(val, str):
                val = val.replace("{symbol}", str(api_symbol))
                val = val.replace("{start_date}", start_date.strftime("%Y%m%d"))
                val = val.replace("{end_date}", end_date.strftime("%Y%m%d"))
                params[key] = val

        # 带重试的HTTP请求
        max_attempts = retry_cfg.get("max_attempt", 3)
        backoff_factor = retry_cfg.get("backoff_factor", 2)
        last_error = None

        for attempt in range(max_attempts):
            try:
                if method == "GET":
                    resp = requests.get(base_url, params=params, headers=headers, timeout=timeout)
                else:
                    resp = requests.post(base_url, json=params, headers=headers, timeout=timeout)
                resp.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < max_attempts - 1:
                    import time
                    time.sleep(backoff_factor ** attempt)
        else:
            raise last_error

        # 解析响应
        content_type = resp.headers.get("Content-Type", "")
        if "json" in content_type or base_url.endswith("json"):
            raw_data = self._parse_json_response(resp.json(), parser_cfg)
        else:
            raw_data = self._parse_text_response(resp.text, parser_cfg)

        if not raw_data:
            logger.warning(f"HTTP API未返回数据: {base_url}")
            return []

        # 转换为统一格式
        records = []
        for row in raw_data:
            record = {
                "date": row.get("date"),
                "open": self._safe_float(row.get("open")),
                "high": self._safe_float(row.get("high")),
                "low": self._safe_float(row.get("low")),
                "close": self._safe_float(row.get("close")),
                "volume": int(self._safe_float(row.get("volume", 0)) or 0),
                "change_pct": self._safe_float(row.get("change_pct")),
                "change_amount": self._safe_float(row.get("change_amount")),
                "amplitude": self._safe_float(row.get("amplitude")),
            }
            records.append(record)

        logger.info(f"HTTP API采集完成: {len(records)} 条记录")
        return records

    def _parse_json_response(self, data: any, parser_cfg: Dict) -> List[Dict]:
        """
        解析JSON响应，支持嵌套路径导航.

        Args:
            data: JSON响应数据
            parser_cfg: 解析器配置

        Returns:
            List[Dict]: 解析后的数据列表
        """
        response_root = parser_cfg.get("response_root", "")

        # 按点分隔的路径导航（如 "data.klines"）
        if response_root:
            for key in response_root.split("."):
                key = key.strip()
                if not key:
                    continue
                if isinstance(data, dict):
                    data = data.get(key)
                elif isinstance(data, list) and key.isdigit():
                    data = data[int(key)]
                if data is None:
                    return []
            # When the path is something like "data.klines", the result might be
            # a list of comma-separated strings, or a list of objects.
            # Only return here if it's already a list.
            if isinstance(data, list):
                rows = data
            elif isinstance(data, dict):
                # Wrapped in another dict -- try to find a list
                data_list_key = parser_cfg.get("data_list_key", "")
                if data_list_key:
                    rows = data.get(data_list_key, [])
                else:
                    rows = list(data.values())[0] if data else []
            else:
                rows = []
        else:
            if isinstance(data, list):
                rows = data
            elif isinstance(data, dict):
                data_list_key = parser_cfg.get("data_list_key", "")
                if data_list_key:
                    rows = data.get(data_list_key, [])
                else:
                    # Try common keys
                    for candidate in ("data", "rows", "records", "items"):
                        if candidate in data:
                            rows = data[candidate]
                            break
                    else:
                        rows = list(data.values())[0] if data else []
            else:
                rows = []

        # 解析每一行
        parsed = []
        date_idx = parser_cfg.get("date_field", 0)
        open_idx = parser_cfg.get("open_field", 1)
        high_idx = parser_cfg.get("high_field", 2)
        low_idx = parser_cfg.get("low_field", 3)
        close_idx = parser_cfg.get("close_field", 4)
        volume_idx = parser_cfg.get("volume_field", 5)
        change_pct_idx = parser_cfg.get("change_pct_field", -1)
        amplitude_idx = parser_cfg.get("amplitude_field", -1)

        for row in rows:
            if isinstance(row, str):
                # CSV行
                fields = row.split(",")
                if len(fields) <= max(date_idx, open_idx, high_idx, low_idx, close_idx):
                    continue
                parsed.append({
                    "date": fields[date_idx].strip(),
                    "open": fields[open_idx].strip(),
                    "high": fields[high_idx].strip(),
                    "low": fields[low_idx].strip(),
                    "close": fields[close_idx].strip(),
                    "volume": fields[volume_idx].strip() if len(fields) > volume_idx else "0",
                    "change_pct": fields[change_pct_idx].strip() if change_pct_idx >= 0 and len(fields) > change_pct_idx else "",
                    "amplitude": fields[amplitude_idx].strip() if amplitude_idx >= 0 and len(fields) > amplitude_idx else "",
                })
            elif isinstance(row, dict):
                # JSON对象 - 按索引或键名提取
                def _get_field(data, idx, default=""):
                    if isinstance(data, dict):
                        # 优先用索引对应的键名查找
                        key_map = {
                            0: "date", 1: "open", 2: "high", 3: "low",
                            4: "close", 5: "volume", 6: "change_pct",
                            7: "change_amount", 8: "amplitude"
                        }
                        key = key_map.get(idx, "")
                        if key and key in data:
                            return data[key]
                        # 回退到值列表
                        values = list(data.values())
                        if idx < len(values):
                            return values[idx]
                    return default

                parsed.append({
                    "date": _get_field(row, date_idx),
                    "open": _get_field(row, open_idx),
                    "high": _get_field(row, high_idx),
                    "low": _get_field(row, low_idx),
                    "close": _get_field(row, close_idx),
                    "volume": _get_field(row, volume_idx, "0"),
                    "change_pct": _get_field(row, change_pct_idx),
                    "change_amount": _get_field(row, 7),
                    "amplitude": _get_field(row, amplitude_idx),
                })
            elif isinstance(row, list):
                # JSON数组行 - 按索引提取
                def _safe_idx(lst, idx, default=""):
                    if idx >= 0 and idx < len(lst):
                        return lst[idx]
                    return default

                parsed.append({
                    "date": _safe_idx(row, date_idx),
                    "open": _safe_idx(row, open_idx),
                    "high": _safe_idx(row, high_idx),
                    "low": _safe_idx(row, low_idx),
                    "close": _safe_idx(row, close_idx),
                    "volume": _safe_idx(row, volume_idx, "0"),
                    "change_pct": _safe_idx(row, change_pct_idx),
                    "amplitude": _safe_idx(row, amplitude_idx),
                })

        return parsed

    def _parse_text_response(self, text: str, parser_cfg: Dict) -> List[Dict]:
        """
        解析纯文本/CSV响应.

        Args:
            text: 响应文本
            parser_cfg: 解析器配置

        Returns:
            List[Dict]: 解析后的数据列表
        """
        lines = text.strip().split("\n")
        # 跳过表头行（如果配置了）
        skip_rows = parser_cfg.get("skip_rows", 0)
        lines = lines[skip_rows:]

        return self._parse_json_response(lines, parser_cfg)

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
            "futures_foreign_hist": self.collect_foreign_futures_daily,
            "crypto_ccxt": self.collect_crypto_daily,
            "bond_cn_daily": self.collect_bond_daily,
            "bond_us_daily": self.collect_bond_us_daily,
            "bond_zh_us_rate": self.collect_bond_us_daily,
            "bond_gb_zh_sina": self.collect_bond_gb_zh_sina,
            "bond_gb_us_sina": self.collect_bond_gb_us_sina,
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
        if interface == "forex_em":
            return await self.fetch_supported_symbols()
        elif interface in ("stock_zh_a_spot_em", "stock_zh_a_spot"):
            return await self._fetch_stock_cn_symbols()
        elif interface in ("stock_us_spot_em", "stock_us_spot"):
            return await self._fetch_stock_us_symbols()
        elif interface in ("stock_hk_spot_em", "stock_hk_spot"):
            return await self._fetch_stock_hk_symbols()
        elif interface == "futures_zh_spot_em":
            return await self._fetch_futures_symbols()
        elif interface == "futures_foreign_sina":
            return await self._fetch_foreign_futures_symbols()
        elif interface == "crypto_ccxt":
            return await self._fetch_crypto_symbols()
        elif interface == "bond_zh_spot_em":
            return await self._fetch_bond_cn_symbols()
        elif interface == "bond_gb_zh_sina":
            return await self._fetch_bond_gb_zh_sina_symbols()
        elif interface == "bond_gb_us_sina":
            return await self._fetch_bond_us_symbols()
        elif interface == "bond_zh_us_rate":
            return await self._fetch_bond_yield_symbols()
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
                df = await asyncio.to_thread(
                    ak.stock_us_daily,
                    symbol=symbol_code.upper(),
                    adjust="",
                )
            elif market == "hk":
                df = await asyncio.to_thread(
                    ak.stock_hk_daily,
                    symbol=symbol_code,
                    adjust="",
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

            # 新浪源返回全量历史, 需要计算涨跌幅/振幅
            df = df.sort_values("date")
            df["change_pct"] = df["close"].pct_change() * 100
            df["change_amount"] = df["close"].diff()
            df["amplitude"] = (df["high"] - df["low"]) / df["close"].shift(1) * 100

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
                    "change_pct": self._safe_float(row.get("change_pct")),
                    "change_amount": self._safe_float(row.get("change_amount")),
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
        采集国内债券收益率数据 (bond_zh_us_rate).

        与美债共用同一接口，根据 symbol_name 匹配对应的收益率列.
        """
        logger.info(f"开始采集国内债券数据: {symbol_name} ({symbol_code}), {start_date} ~ {end_date}")
        try:
            return await asyncio.wait_for(
                self._call_bond_yield(symbol_name, symbol_code, start_date, end_date, "cn"),
                timeout=45
            )
        except asyncio.TimeoutError:
            raise Exception(f"国内债券采集超时(45s): {symbol_name}")
        except Exception:
            raise

    async def collect_bond_us_daily(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        采集美国债券收益率数据 (bond_zh_us_rate).

        与国内债券共用同一接口，根据 symbol_name 匹配对应的收益率列.
        """
        logger.info(f"开始采集美国债券数据: {symbol_name} ({symbol_code}), {start_date} ~ {end_date}")

        try:
            records = await asyncio.wait_for(
                self._call_bond_yield(symbol_name, symbol_code, start_date, end_date, "us"),
                timeout=45
            )
            if records:
                logger.info(f"bond_zh_us_rate 成功采集 {len(records)} 条 {symbol_name} 数据")
                return records
            logger.warning(f"bond_zh_us_rate 返回空数据: {symbol_name}")
        except asyncio.TimeoutError:
            logger.error(f"bond_zh_us_rate 超时(45s): {symbol_name}")
        except Exception as e:
            logger.error(f"bond_zh_us_rate 采集失败: {symbol_name}, {str(e)[:120]}")

        raise Exception(f"债券数据源采集失败 {symbol_name}: bond_zh_us_rate 不可用")

    async def collect_bond_gb_zh_sina(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        采集中国国债收益率数据 (bond_gb_zh_sina, 新浪源).

        返回标准OHLC格式，open/high/low/close 均为收益率值.
        """
        import akshare as ak
        import pandas as pd

        logger.info(f"开始采集中国国债(sina): {symbol_name}, {start_date} ~ {end_date}")
        df = await asyncio.wait_for(
            asyncio.to_thread(ak.bond_gb_zh_sina, symbol=symbol_name), timeout=30
        )
        if df is None or df.empty:
            return []

        df = df.rename(columns={"date": "date"}) if "date" in df.columns else df
        if "日期" in df.columns:
            df = df.rename(columns={"日期": "date"})
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
        df = df.sort_values("date")

        records = []
        for _, row in df.iterrows():
            records.append({
                "date": row["date"].strftime("%Y-%m-%d"),
                "open": self._safe_float(row.get("open")),
                "high": self._safe_float(row.get("high")),
                "low": self._safe_float(row.get("low")),
                "close": self._safe_float(row.get("close")),
                "volume": int(self._safe_float(row.get("volume", 0)) or 0),
            })
        logger.info(f"bond_gb_zh_sina 成功采集 {len(records)} 条 {symbol_name}")
        return records

    async def collect_bond_gb_us_sina(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        采集美国国债收益率数据 (bond_gb_us_sina, 新浪源).

        返回标准OHLC格式，open/high/low/close 均为收益率值.
        """
        import akshare as ak
        import pandas as pd

        logger.info(f"开始采集美国国债(sina): {symbol_name}, {start_date} ~ {end_date}")
        df = await asyncio.wait_for(
            asyncio.to_thread(ak.bond_gb_us_sina, symbol=symbol_name), timeout=30
        )
        if df is None or df.empty:
            return []

        df = df.rename(columns={"date": "date"}) if "date" in df.columns else df
        if "日期" in df.columns:
            df = df.rename(columns={"日期": "date"})
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
        df = df.sort_values("date")

        records = []
        for _, row in df.iterrows():
            records.append({
                "date": row["date"].strftime("%Y-%m-%d"),
                "open": self._safe_float(row.get("open")),
                "high": self._safe_float(row.get("high")),
                "low": self._safe_float(row.get("low")),
                "close": self._safe_float(row.get("close")),
                "volume": int(self._safe_float(row.get("volume", 0)) or 0),
            })
        logger.info(f"bond_gb_us_sina 成功采集 {len(records)} 条 {symbol_name}")
        return records

    async def _call_bond_yield(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
        market: str = "us",
    ) -> List[Dict]:
        """
        统一债券收益率采集 (bond_zh_us_rate).

        单次调用返回中美两国各期限收益率, 根据 symbol_name 提取对应列.
        数据量~9300条从1990年至今.

        Args:
            symbol_name: 债券名称（如"美国10年期国债" / "中国国债收益率10年"）
            symbol_code: 债券代码
            start_date: 开始日期
            end_date: 结束日期
            market: cn/us

        Returns:
            List[Dict]: OHLC格式的收益率数据
        """
        import akshare as ak
        import pandas as pd

        # 名称→列名映射
        column_map = {
            # 中国国债
            "中国国债收益率2年": "中国国债收益率2年",
            "中国国债收益率5年": "中国国债收益率5年",
            "中国国债收益率10年": "中国国债收益率10年",
            "中国国债收益率30年": "中国国债收益率30年",
            # 美国国债
            "美国国债收益率2年": "美国国债收益率2年",
            "美国国债收益率5年": "美国国债收益率5年",
            "美国国债收益率10年": "美国国债收益率10年",
            "美国国债收益率30年": "美国国债收益率30年",
        }

        # 兼容旧的 symbol_name 格式
        legacy_map = {
            "美国10年期国债": "美国国债收益率10年",
            "美国2年期国债": "美国国债收益率2年",
            "美国5年期国债": "美国国债收益率5年",
            "美国30年期国债": "美国国债收益率30年",
            "中国10年期国债": "中国国债收益率10年",
            "中国2年期国债": "中国国债收益率2年",
            "中国5年期国债": "中国国债收益率5年",
        }

        rate_column = column_map.get(symbol_name) or legacy_map.get(symbol_name)
        if not rate_column:
            for name, col in {**column_map, **legacy_map}.items():
                if name in symbol_name or (symbol_name in name):
                    rate_column = col
                    break
        if not rate_column:
            raise ValueError(f"无法匹配债券期限: {symbol_name}")

        df = await asyncio.wait_for(asyncio.to_thread(ak.bond_zh_us_rate), timeout=30)

        if df is None or df.empty:
            return []

        if rate_column not in df.columns:
            raise ValueError(f"中美利差数据中无 '{rate_column}' 列，可用列: {df.columns.tolist()}")

        # 提取日期和目标列，转换为OHLC格式
        df = df[["日期", rate_column]].copy()
        df = df.rename(columns={"日期": "date", rate_column: "close"})
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
        df = df.sort_values("date")

        if df.empty:
            return []

        df["open"] = df["close"]
        df["high"] = df["close"]
        df["low"] = df["close"]
        df["volume"] = 0

        if len(df) >= 2:
            df["change_pct"] = df["close"].pct_change() * 100
            df["change_amount"] = df["close"].diff()

        records = []
        for _, row in df.iterrows():
            records.append({
                "date": row["date"].strftime("%Y-%m-%d"),
                "open": self._safe_float(row.get("open")),
                "high": self._safe_float(row.get("high")),
                "low": self._safe_float(row.get("low")),
                "close": self._safe_float(row.get("close")),
                "volume": int(self._safe_float(row.get("volume", 0)) or 0),
                "change_pct": self._safe_float(row.get("change_pct") if "change_pct" in row.index else None),
                "change_amount": self._safe_float(row.get("change_amount") if "change_amount" in row.index else None),
            })
        return records

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
                if not symbol_code.lower().startswith(("sh", "sz", "bj")):
                    symbol_code = ("sh" if symbol_code.startswith("0") or symbol_code.startswith("1") else "sz") + symbol_code
                df = await asyncio.wait_for(asyncio.to_thread(ak.bond_zh_hs_daily, symbol=symbol_code), timeout=30)
            elif market == "us":
                # 美债不再走此路径, 统一走 collect_bond_us_daily → bond_zh_us_rate
                raise ValueError("美债请使用 bond_zh_us_rate 接口")
            else:
                raise ValueError(f"不支持的债券市场: {market}")

            if df is None or df.empty:
                return []

            # 过滤日期范围
            df["date"] = pd.to_datetime(df["date"])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)]

            if df.empty:
                return []

            # 新浪源不提供涨跌幅，需计算
            df = df.sort_values("date")
            df["change_pct"] = df["close"].pct_change() * 100
            df["change_amount"] = df["close"].diff()

            records = []
            for _, row in df.iterrows():
                record = {
                    "date": pd.to_datetime(row["date"]).strftime("%Y-%m-%d"),
                    "open": self._safe_float(row.get("open")),
                    "high": self._safe_float(row.get("high")),
                    "low": self._safe_float(row.get("low")),
                    "close": self._safe_float(row.get("close")),
                    "volume": int(self._safe_float(row.get("volume", 0)) or 0),
                    "change_pct": self._safe_float(row.get("change_pct")),
                    "change_amount": self._safe_float(row.get("change_amount")),
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
        # 从合约代码提取品种代码（如 AU9999 → AU0, IF9999 → IF0）
        import re
        variety_match = re.match(r'^([A-Za-z]+)', symbol_code)
        sina_symbol = f"{variety_match.group(1)}0" if variety_match else symbol_code

        logger.info(f"开始采集期货数据: {symbol_name} ({symbol_code}->{sina_symbol}), {start_date} ~ {end_date}")

        try:
            df = await asyncio.to_thread(
                self._call_futures_daily,
                sina_symbol,
                start_date,
                end_date,
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

    def _transform_futures_data(self, df, symbol_code: str) -> List[Dict]:
        """将 futures_main_sina 返回的 DataFrame 转换为标准 OHLC 记录."""
        from datetime import date as DateType
        records = []
        for _, row in df.iterrows():
            date_val = row["date"]
            if hasattr(date_val, "date"):
                date_val = date_val.date()
            elif hasattr(date_val, "strftime"):
                date_val = DateType.fromisoformat(date_val.strftime("%Y-%m-%d"))
            else:
                date_val = DateType.fromisoformat(str(date_val)[:10])
            records.append({
                "date": date_val,
                "open": self._safe_float(row.get("open")),
                "high": self._safe_float(row.get("high")),
                "low": self._safe_float(row.get("low")),
                "close": self._safe_float(row.get("close")),
                "volume": int(self._safe_float(row.get("volume", 0)) or 0),
                "open_interest": int(self._safe_float(row.get("open_interest", 0)) or 0),
                "settle_price": self._safe_float(row.get("settle_price")),
            })
        return records

    def _call_futures_daily(
        self,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ):
        """
        调用AKShare get_futures_daily 获取期货数据.

        注意: futures_zh_daily_sina (新浪源) 在 akshare 1.18.55 不可用.
        get_futures_daily 当前仅覆盖 CFFEX 金融期货 (IF/IC/IH/IM/T/TF/TL/TS).

        Args:
            symbol_code: 期货品种代码（如 IF, RB, M）
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame: API返回的数据，若无数据返回空DataFrame
        """
        import akshare as ak
        import pandas as pd

        # futures_main_sina 覆盖6大交易所82个品种
        df = ak.futures_main_sina(
            symbol=symbol_code,
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
        )

        if df is None or df.empty:
            return pd.DataFrame()

        # 统一列名为英文
        df = df.rename(columns={
            "日期": "date", "开盘价": "open", "最高价": "high",
            "最低价": "low", "收盘价": "close", "成交量": "volume",
            "持仓量": "open_interest", "动态结算价": "settle_price",
        })
        df["date"] = pd.to_datetime(df["date"])

        return df

    async def _fetch_stock_cn_symbols(self) -> List[Dict]:
        """获取A股标的列表（新浪源 stock_zh_a_spot，5511只）."""
        try:
            import akshare as ak
            import pandas as pd

            # 新浪源A股实时行情（stock_zh_a_spot_em 东方财富源被封不可用）
            df = await asyncio.to_thread(ak.stock_zh_a_spot)

            # 转换为统一格式
            records = []
            for _, row in df.iterrows():
                raw_code = str(row.get("代码", ""))
                # 新浪源代码带交易所前缀 (sh600519, sz000001, bj920000)
                if raw_code.startswith("sh"):
                    exchange = "sh"
                    code = raw_code[2:]
                elif raw_code.startswith("sz"):
                    exchange = "sz"
                    code = raw_code[2:]
                elif raw_code.startswith("bj"):
                    exchange = "bj"
                    code = raw_code[2:]
                elif raw_code.startswith("6"):
                    exchange = "sh"
                    code = raw_code
                elif raw_code.startswith(("0", "3")):
                    exchange = "sz"
                    code = raw_code
                elif raw_code.startswith(("4", "8")):
                    exchange = "bj"
                    code = raw_code
                else:
                    exchange = "sz"
                    code = raw_code

                if code and code.isdigit():
                    records.append({
                        "code": code.zfill(6),
                        "name": str(row.get("名称", "")),
                        "exchange": exchange,
                        "market_code": "stock_cn",
                    })

            logger.info(f"获取A股标的列表成功，共 {len(records)} 条")
            return records

        except Exception as e:
            logger.warning(f"获取A股标的列表失败，使用默认列表: {e}")
            return self._get_default_stock_cn_symbols()

    async def _fetch_stock_us_symbols(self) -> List[Dict]:
        """获取美股标的列表（60s超时回退到默认列表）."""
        try:
            import akshare as ak
            df = await asyncio.wait_for(asyncio.to_thread(ak.get_us_stock_name), timeout=60)
            records = []
            for _, row in df.iterrows():
                records.append({
                    "code": str(row.get("code", "")).lower(),
                    "name": str(row.get("name", "")),
                    "exchange": "nasdaq",
                    "market_code": "stock_us",
                })
            logger.info(f"获取美股标的列表成功，共 {len(records)} 条")
            return records
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning(f"获取美股标的列表失败/超时，使用默认列表: {e}")
            return self._get_default_us_symbols()

    async def _fetch_stock_hk_symbols(self) -> List[Dict]:
        """获取港股标的列表."""
        try:
            import akshare as ak
            df = await asyncio.to_thread(ak.stock_hk_spot)
            records = []
            for _, row in df.iterrows():
                records.append({
                    "code": str(row.get("代码", "")),
                    "name": str(row.get("中文名称", "")),
                    "exchange": "hkex",
                    "market_code": "stock_hk",
                })
            logger.info(f"获取港股标的列表成功，共 {len(records)} 条")
            return records
        except Exception as e:
            logger.warning(f"获取港股标的列表失败，使用默认列表: {e}")
            return self._get_default_hk_symbols()

    async def collect_foreign_futures_daily(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        采集国际期货日线数据 (futures_foreign_hist, 新浪源).

        覆盖COMEX/CME/NYMEX/LME/ICE/CBOT等30个品种.
        """
        import akshare as ak
        import pandas as pd
        from datetime import date as dt_date

        # 提取品种代码（如 XAU9999 → XAU, CL9999 → CL）
        import re
        variety_match = re.match(r'^([A-Za-z]+)', symbol_code)
        api_symbol = variety_match.group(1) if variety_match else symbol_code

        logger.info(f"开始采集国际期货: {symbol_name} ({symbol_code}→{api_symbol}), {start_date} ~ {end_date}")
        df = await asyncio.wait_for(
            asyncio.to_thread(ak.futures_foreign_hist, symbol=api_symbol), timeout=30
        )
        if df is None or df.empty:
            return []

        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
        df = df.sort_values("date")

        records = []
        for _, row in df.iterrows():
            date_val = row["date"]
            if hasattr(date_val, "date"):
                date_val = date_val.date()
            else:
                date_val = dt_date.fromisoformat(str(date_val)[:10])
            records.append({
                "date": date_val,
                "open": self._safe_float(row.get("open")),
                "high": self._safe_float(row.get("high")),
                "low": self._safe_float(row.get("low")),
                "close": self._safe_float(row.get("close")),
                "volume": int(self._safe_float(row.get("volume", 0)) or 0),
            })
        logger.info(f"futures_foreign_hist 成功采集 {len(records)} 条 {symbol_name}")
        return records

    async def collect_crypto_daily(
        self,
        symbol_name: str,
        symbol_code: str,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        采集数字货币日线数据 (CCXT, Kraken优先).

        免费无需API Key，日线OHLCV数据.
        """
        import ccxt
        from datetime import date as dt_date

        logger.info(f"开始采集数字货币: {symbol_name} ({symbol_code}), {start_date} ~ {end_date}")

        # Kraken优先（无地域限制），Binance备选
        ohlcv = []
        for ex_id in ["kraken", "binance", "coinbase"]:
            try:
                exchange = getattr(ccxt, ex_id)()
                since_ts = int(__import__('calendar').timegm(start_date.timetuple()) * 1000)
                ohlcv = await asyncio.wait_for(
                    asyncio.to_thread(exchange.fetch_ohlcv, symbol_code, "1d", since_ts, 1000),
                    timeout=30
                )
                if ohlcv:
                    logger.info(f"CCXT {ex_id} 成功获取 {len(ohlcv)} 条 {symbol_code}")
                    break
            except Exception as e:
                logger.warning(f"CCXT {ex_id} 失败: {str(e)[:80]}")
                continue

        if not ohlcv:
            return []

        records = []
        for candle in ohlcv:
            ts, o, h, l, c, v = candle[:6]
            record_date = dt_date.fromtimestamp(ts / 1000)
            if record_date < start_date or record_date > end_date:
                continue
            records.append({
                "date": record_date,
                "open": self._safe_float(o),
                "high": self._safe_float(h),
                "low": self._safe_float(l),
                "close": self._safe_float(c),
                "volume": int(v or 0),
            })
        logger.info(f"CCXT 成功采集 {len(records)} 条 {symbol_name}")
        return records

    async def _fetch_crypto_symbols(self) -> List[Dict]:
        """获取主流数字货币交易对列表."""
        symbols = [
            ("BTC/USDT", "比特币"), ("ETH/USDT", "以太坊"), ("SOL/USDT", "Solana"),
            ("XRP/USDT", "瑞波币"), ("DOGE/USDT", "狗狗币"), ("ADA/USDT", "艾达币"),
            ("AVAX/USDT", "Avalanche"), ("DOT/USDT", "波卡"), ("LINK/USDT", "Chainlink"),
            ("MATIC/USDT", "Polygon"), ("UNI/USDT", "Uniswap"), ("ATOM/USDT", "Cosmos"),
            ("LTC/USDT", "莱特币"), ("ETC/USDT", "以太经典"), ("BCH/USDT", "比特现金"),
            ("FIL/USDT", "Filecoin"), ("APT/USDT", "Aptos"), ("ARB/USDT", "Arbitrum"),
            ("OP/USDT", "Optimism"), ("NEAR/USDT", "NEAR Protocol"),
        ]
        records = []
        for code, name in symbols:
            records.append({"code": code, "name": name, "market_code": "crypto"})
        logger.info(f"获取数字货币标的列表成功，共 {len(records)} 条")
        return records

    async def _fetch_foreign_futures_symbols(self) -> List[Dict]:
        """获取国际期货标的列表（新浪外盘 futures_foreign_commodity_subscribe_exchange_symbol）."""
        import akshare as ak

        syms = ak.futures_foreign_commodity_subscribe_exchange_symbol()
        detail_df = ak.futures_hq_subscribe_exchange_symbol()
        # 建立 code→name 映射 (列名: symbol=中文名, code=英文代码)
        name_map = {}
        for _, row in detail_df.iterrows():
            name_map[str(row.get("code", ""))] = str(row.get("symbol", ""))

        records = []
        for sym in syms:
            name = name_map.get(sym, sym)
            records.append({
                "code": sym,
                "name": name,
                "exchange": "global",
                "market_code": "futures_intl",
            })
        logger.info(f"获取国际期货标的列表成功，共 {len(records)} 条")
        return records

    async def _fetch_futures_symbols(self) -> List[Dict]:
        """获取国内期货主力连续合约标的列表（futures_display_main_sina，覆盖6大交易所）."""
        import akshare as ak

        df = await asyncio.to_thread(ak.futures_display_main_sina)
        records = []
        for _, row in df.iterrows():
            symbol = str(row.get("symbol", ""))
            name = str(row.get("name", ""))
            exchange = str(row.get("exchange", "")).upper()
            records.append({
                "code": symbol,  # 如 AU0, IF0
                "name": name,     # 如 黄金连续, 沪深300指数期货连续
                "exchange": exchange,
                "variety": symbol.rstrip("0"),  # 品种代码: AU, IF
                "market_code": "futures_cn",
            })
        logger.info(f"获取期货主力合约列表成功，共 {len(records)} 条")
        return records

    def _get_default_us_symbols(self) -> List[Dict]:
        """美股默认标的列表（API超时或不可用时的回退，覆盖主要行业龙头）."""
        symbols = [
            # 科技
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX", "ADBE", "CRM",
            "ORCL", "CSCO", "INTC", "AMD", "QCOM", "TXN", "AVGO", "IBM", "INTU", "NOW",
            # 金融
            "JPM", "BAC", "WFC", "C", "GS", "MS", "V", "MA", "AXP", "BLK",
            # 消费
            "WMT", "PG", "KO", "PEP", "COST", "MCD", "NKE", "SBUX", "HD", "LOW",
            # 医疗
            "JNJ", "PFE", "MRK", "ABBV", "UNH", "ABT", "LLY", "TMO", "DHR", "BMY",
            # 工业/能源
            "XOM", "CVX", "BA", "CAT", "GE", "HON", "UPS", "RTX", "LMT", "DE",
            # 通信/媒体
            "DIS", "CMCSA", "T", "VZ", "CHTR",
            # 其他
            "BRK.B", "SPY", "QQQ",
        ]
        return [{"code": s.lower(), "name": s, "exchange": "nasdaq", "market_code": "stock_us"} for s in symbols]

    def _get_default_hk_symbols(self) -> List[Dict]:
        """港股默认标的列表（API不可用时的回退）."""
        symbols = [
            ("00700", "腾讯控股"), ("09988", "阿里巴巴"), ("09999", "网易"),
            ("00941", "中国移动"), ("02318", "中国平安"), ("03988", "中国银行"),
            ("00005", "汇丰控股"), ("00388", "香港交易所"), ("01810", "小米集团"),
            ("01024", "快手"), ("02015", "理想汽车"), ("09618", "京东集团"),
        ]
        return [{"code": c, "name": n, "exchange": "hkex", "market_code": "stock_hk"} for c, n in symbols]

    def _get_default_bond_cn_symbols(self) -> List[Dict]:
        """国内债券默认标的列表（API不可用时的回退）."""
        symbols = [
            ("sh019678", "22国债13"), ("sh019688", "22国债23"), ("sh019696", "23国债03"),
            ("sh113044", "大秦转债"), ("sh110059", "浦发转债"), ("sh113011", "光大转债"),
            ("sz127015", "希望转债"), ("sz128119", "龙净转债"),
        ]
        return [{"code": c, "name": n, "exchange": "sh" if c.startswith("sh") else "sz", "market_code": "bond_cn"} for c, n in symbols]

    async def _fetch_bond_gb_zh_sina_symbols(self) -> List[Dict]:
        """获取中国国债标的列表（新浪源 bond_gb_zh_sina）."""
        cn_bond_symbols = [
            {"code": "中国1年期国债", "name": "中国1年期国债", "market_code": "bond_cn"},
            {"code": "中国2年期国债", "name": "中国2年期国债", "market_code": "bond_cn"},
            {"code": "中国3年期国债", "name": "中国3年期国债", "market_code": "bond_cn"},
            {"code": "中国5年期国债", "name": "中国5年期国债", "market_code": "bond_cn"},
            {"code": "中国7年期国债", "name": "中国7年期国债", "market_code": "bond_cn"},
            {"code": "中国10年期国债", "name": "中国10年期国债", "market_code": "bond_cn"},
            {"code": "中国30年期国债", "name": "中国30年期国债", "market_code": "bond_cn"},
        ]
        logger.info(f"获取中国国债标的(sina)成功，共 {len(cn_bond_symbols)} 条")
        return cn_bond_symbols

    async def _fetch_bond_cn_symbols(self) -> List[Dict]:
        """获取国内债券标的列表."""
        try:
            import akshare as ak
            df = await asyncio.to_thread(ak.bond_zh_hs_cov_spot)
            records = []
            for _, row in df.iterrows():
                records.append({
                    "code": str(row.get("code", "")),
                    "name": str(row.get("name", "")),
                    "exchange": "sh" if str(row.get("code", "")).startswith("1") else "sz",
                    "market_code": "bond_cn",
                })
            if records:
                logger.info(f"获取国内债券标的列表成功，共 {len(records)} 条")
                return records
        except Exception as e:
            logger.warning(f"获取国内债券标的列表失败，使用默认列表: {e}")
        return self._get_default_bond_cn_symbols()

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


    async def _fetch_bond_yield_symbols(self) -> List[Dict]:
        """从 bond_zh_us_rate API 动态获取收益率列名作为标的."""
        import akshare as ak
        try:
            df = await asyncio.wait_for(asyncio.to_thread(ak.bond_zh_us_rate), timeout=30)
            if df is None or df.empty:
                logger.warning("bond_zh_us_rate 返回空数据, 使用预定义标的列表")
                return self._bond_yield_fallback_symbols()

            # 过滤出收益率相关列名（排除日期、GDP等非收益率列）
            exclude = {'日期', '中国GDP年增率', '美国GDP年增率'}
            columns = [c for c in df.columns if c not in exclude]
            symbols = [{"code": col, "name": col} for col in columns]
            logger.info(f"从 bond_zh_us_rate 动态获取 {len(symbols)} 个标的")
            return symbols
        except Exception as e:
            logger.warning(f"bond_zh_us_rate 标获取失败: {e}, 使用预定义列表")
            return self._bond_yield_fallback_symbols()

    def _bond_yield_fallback_symbols(self) -> List[Dict]:
        """预定义债券收益率标的列表（API 不可用时的回退）."""
        return [
            {"code": "中国国债收益率2年", "name": "中国国债收益率2年"},
            {"code": "中国国债收益率5年", "name": "中国国债收益率5年"},
            {"code": "中国国债收益率10年", "name": "中国国债收益率10年"},
            {"code": "中国国债收益率30年", "name": "中国国债收益率30年"},
            {"code": "美国国债收益率2年", "name": "美国国债收益率2年"},
            {"code": "美国国债收益率5年", "name": "美国国债收益率5年"},
            {"code": "美国国债收益率10年", "name": "美国国债收益率10年"},
            {"code": "美国国债收益率30年", "name": "美国国债收益率30年"},
        ]


# 全局采集器实例
akshare_collector = AKShareCollector()