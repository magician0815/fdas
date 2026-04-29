"""
数据源配置Schema验证.

定义数据源配置JSON的Pydantic验证模型，支持多采集器类型.

Author: FDAS Team
Created: 2026-04-21
Updated: 2026-04-23 - 新增多采集器类型支持
"""

from typing import Optional, Dict, Any, Literal, Tuple
from pydantic import BaseModel, Field, model_validator
import json


class APIConfig(BaseModel):
    """API配置（http_api类型使用）."""
    base_url: str = Field(..., description="API基础URL")
    method: str = "GET"
    timeout: int = 30
    retry: Optional[Dict[str, Any]] = Field(default=None, description="重试配置")


class DataParserConfig(BaseModel):
    """数据解析配置（http_api类型使用）."""
    response_root: str = Field(..., description="响应数据根路径")
    date_field: int = Field(..., description="日期字段索引")
    open_field: int = Field(..., description="开盘价字段索引")
    high_field: int = Field(..., description="最高价字段索引")
    low_field: int = Field(..., description="最低价字段索引")
    close_field: int = Field(..., description="收盘价字段索引")
    volume_field: int = Field(default=5, description="成交量字段索引")


class SymbolFetchConfig(BaseModel):
    """标的获取配置."""
    interface: str = Field(..., description="AKShare接口名")
    result_key: Optional[str] = Field(None, description="结果数据键名")
    code_field: str = Field(..., description="代码字段名")
    name_field: str = Field(..., description="名称字段名")


class AKShareParamsConfig(BaseModel):
    """AKShare参数配置."""
    symbol: Optional[str] = Field(None, description="标的代码")
    period: Optional[str] = Field(None, description="周期（daily/weekly/monthly）")
    start_date: Optional[str] = Field(None, description="开始日期（YYYYMMDD）")
    end_date: Optional[str] = Field(None, description="结束日期（YYYYMMDD）")
    adjust: Optional[str] = Field(None, description="复权类型（qfq/hfdf/空）")


class DatasourceConfigSchema(BaseModel):
    """数据源配置文件Schema."""
    version: str = "1.0"
    name: str = Field(..., description="数据源名称")
    type: str = Field(..., description="���据源类型（如akshare）")
    market: str = Field(..., description="市场类型（如forex, stock_cn）")

    # 采集器类型
    collector_type: Literal["http_api", "akshare_native"] = Field(
        default="akshare_native",
        description="采集器类型：http_api=自定义API，akshare_native=AKShare原生接口"
    )

    # http_api 类型配置
    api: Optional[APIConfig] = Field(default=None, description="API配置（http_api类型使用）")
    headers: Optional[Dict[str, str]] = Field(default=None, description="请求头")
    params: Optional[Dict[str, Any]] = Field(default=None, description="请求参数")
    symbol_mapping: Optional[Dict[str, str]] = Field(default=None, description="标的代码映射")
    data_parser: Optional[DataParserConfig] = Field(default=None, description="数据解析配置")

    # akshare_native 类型配置
    akshare_interface: Optional[str] = Field(default=None, description="AKShare接口名称")
    akshare_params: Optional[AKShareParamsConfig] = Field(default=None, description="AKShare参数")
    symbol_fetch: Optional[SymbolFetchConfig] = Field(default=None, description="标的获取配置")

    @model_validator(mode="after")
    def validate_collector_config(self):
        """根据collector_type验证必要配置."""
        if self.collector_type == "http_api":
            if not self.api:
                raise ValueError("http_api类型必须配置api")
            if not self.data_parser:
                raise ValueError("http_api类型必须配置data_parser")
        elif self.collector_type == "akshare_native":
            if not self.akshare_interface:
                raise ValueError("akshare_native类型必须配置akshare_interface")
        return self

    class Config:
        json_schema_extra = {
            "example_http_api": {
                "version": "1.0",
                "name": "自定义外汇数据源",
                "type": "akshare",
                "market": "forex",
                "collector_type": "http_api",
                "api": {
                    "base_url": "https://api.example.com/forex",
                    "method": "GET",
                    "timeout": 30
                },
                "data_parser": {
                    "response_root": "data",
                    "date_field": 0,
                    "open_field": 1,
                    "high_field": 2,
                    "low_field": 3,
                    "close_field": 4,
                    "volume_field": 5
                }
            },
            "example_akshare_native": {
                "version": "1.0",
                "name": "AKShare A股数据源",
                "type": "akshare",
                "market": "stock_cn",
                "collector_type": "akshare_native",
                "akshare_interface": "stock_zh_a_hist",
                "akshare_params": {
                    "symbol": "000001",
                    "period": "daily",
                    "adjust": ""
                },
                "symbol_fetch": {
                    "interface": "stock_zh_a_spot_em",
                    "result_key": "data",
                    "code_field": "代码",
                    "name_field": "名称"
                }
            }
        }


def validate_config_json(config_json: str) -> Tuple[bool, str, Optional[dict]]:
    """
    验证���置文件JSON是否有效。

    Args:
        config_json: 配置JSON字符串

    Returns:
        (是否有效, 错误消息, 解析后的配置dict)
    """
    try:
        config_dict = json.loads(config_json)
        validated = DatasourceConfigSchema(**config_dict)
        return True, "", validated.model_dump()
    except json.JSONDecodeError as e:
        return False, f"JSON解析错误: {str(e)}", None
    except Exception as e:
        return False, f"配置验证错误: {str(e)}", None


def get_default_forex_config() -> str:
    """获取默认外汇数据源配置JSON。"""
    config = {
        "version": "1.0",
        "name": "东方财富外汇数据源",
        "type": "akshare",
        "market": "forex",
        "collector_type": "http_api",
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
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        },
        "params": {
            "fields1": "f1,f2,f3,f4,f5,f6",
            "field2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
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
            "AUDJPY": "133.AUDJPY"
        },
        "data_parser": {
            "response_root": "data.klines",
            "date_field": 0,
            "open_field": 1,
            "high_field": 2,
            "low_field": 3,
            "close_field": 4,
            "volume_field": 5
        }
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


def get_default_stock_cn_config() -> str:
    """获取默认A股数据源配置JSON。"""
    config = {
        "version": "1.0",
        "name": "AKShare A股历史数据",
        "type": "akshare",
        "market": "stock_cn",
        "collector_type": "akshare_native",
        "akshare_interface": "stock_zh_a_hist",
        "akshare_params": {
            "symbol": "000001",
            "period": "daily",
            "start_date": "20240101",
            "end_date": "20241231",
            "adjust": ""
        },
        "symbol_fetch": {
            "interface": "stock_zh_a_spot_em",
            "result_key": "data",
            "code_field": "代码",
            "name_field": "名称"
        }
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


def get_default_stock_us_config() -> str:
    """获取默认美股数据源配置JSON。"""
    config = {
        "version": "1.0",
        "name": "AKShare 美股历史数据",
        "type": "akshare",
        "market": "stock_us",
        "collector_type": "akshare_native",
        "akshare_interface": "stock_us_daily",
        "akshare_params": {
            "symbol": "AAPL",
            "period": "daily"
        },
        "symbol_fetch": {
            "interface": "stock_us_spot_em",
            "result_key": "data",
            "code_field": "代码",
            "name_field": "名称"
        }
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


def get_default_stock_hk_config() -> str:
    """获取默认港股数据源配置JSON。"""
    config = {
        "version": "1.0",
        "name": "AKShare 港股历史数据",
        "type": "akshare",
        "market": "stock_hk",
        "collector_type": "akshare_native",
        "akshare_interface": "stock_hk_daily",
        "akshare_params": {
            "symbol": "00700"
        },
        "symbol_fetch": {
            "interface": "stock_hk_spot_em",
            "result_key": "data",
            "code_field": "代码",
            "name_field": "名称"
        }
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


def get_default_futures_cn_config() -> str:
    """获取默认国内期货数据源配置JSON。"""
    config = {
        "version": "1.0",
        "name": "AKShare 国内期货历史数据",
        "type": "akshare",
        "market": "futures_cn",
        "collector_type": "akshare_native",
        "akshare_interface": "futures_zh_daily_sina",
        "akshare_params": {
            "symbol": "IF9999"
        },
        "symbol_fetch": {
            "interface": "futures_zh_spot_em",
            "result_key": "data",
            "code_field": "合约代码",
            "name_field": "合约名称"
        }
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


def get_default_bond_cn_config() -> str:
    """获取默认国内债券数据源配置JSON。"""
    config = {
        "version": "1.0",
        "name": "AKShare 国内债券历史数据",
        "type": "akshare",
        "market": "bond_cn",
        "collector_type": "akshare_native",
        "akshare_interface": "bond_cn_daily",
        "akshare_params": {
            "symbol": "113052"
        },
        "symbol_fetch": {
            "interface": "bond_zh_spot_em",
            "result_key": "data",
            "code_field": "债券代码",
            "name_field": "债券名称"
        }
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


def get_default_bond_us_config() -> str:
    """获取默认美国债券数据源配置JSON。"""
    config = {
        "version": "1.0",
        "name": "AKShare 美国债���历史数据",
        "type": "akshare",
        "market": "bond_us",
        "collector_type": "akshare_native",
        "akshare_interface": "bond_us_daily",
        "akshare_params": {
            "symbol": "US10Y"
        },
        "symbol_fetch": {
            "interface": "bond_us_spot_em",
            "result_key": "data",
            "code_field": "债券代码",
            "name_field": "债券名称"
        }
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


def get_default_config(market_code: str) -> str:
    """
    根据市场代码获取默认配置JSON。

    Args:
        market_code: 市场代码（forex/stock_cn/stock_us/stock_hk/futures_cn/bond_cn/bond_us）

    Returns:
        默认配置JSON字符串
    """
    config_map = {
        "forex": get_default_forex_config,
        "stock_cn": get_default_stock_cn_config,
        "stock_us": get_default_stock_us_config,
        "stock_hk": get_default_stock_hk_config,
        "futures_cn": get_default_futures_cn_config,
        "bond_cn": get_default_bond_cn_config,
        "bond_us": get_default_bond_us_config,
    }

    config_func = config_map.get(market_code)
    if config_func:
        return config_func()

    # 默认返回外汇配置
    return get_default_forex_config()