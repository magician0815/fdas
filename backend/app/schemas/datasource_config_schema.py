"""
数据源配置Schema验证.

定义数据源配置JSON的Pydantic验证模型.

Author: FDAS Team
Created: 2026-04-21
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class APIConfig(BaseModel):
    """API配置."""
    base_url: str = Field(..., description="API基础URL")
    method: str = "GET"
    timeout: int = 30
    retry: Optional[Dict[str, Any]] = Field(default=None, description="重试配置")


class DataParserConfig(BaseModel):
    """数据解析配置."""
    response_root: str = Field(..., description="响应数据根路径")
    date_field: int = Field(..., description="日期字段索引")
    open_field: int = Field(..., description="开盘价字段索引")
    high_field: int = Field(..., description="最高价字段索引")
    low_field: int = Field(..., description="最低价字段索引")
    close_field: int = Field(..., description="收盘价字段索引")
    volume_field: int = Field(default=5, description="成交量字段索引")


class DatasourceConfigSchema(BaseModel):
    """数据源配置文件Schema."""
    version: str = "1.0"
    name: str = Field(..., description="数据源名称")
    type: str = Field(..., description="数据源类型（如akshare）")
    market: str = Field(..., description="市场类型（如forex）")
    api: APIConfig
    headers: Dict[str, str] = Field(default_factory=dict, description="请求头")
    params: Optional[Dict[str, Any]] = Field(default=None, description="请求参数")
    symbol_mapping: Optional[Dict[str, str]] = Field(default=None, description="货币对代码映射")
    data_parser: DataParserConfig

    class Config:
        json_schema_extra = {
            "example": {
                "version": "1.0",
                "name": "东方财富外汇数据源",
                "type": "akshare",
                "market": "forex",
                "api": {
                    "base_url": "https://push2his.eastmoney.com/api/qt/stock/kline/get",
                    "method": "GET",
                    "timeout": 30,
                    "retry": {"max_attempt": 3, "backoff_factor": 2}
                },
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://quote.eastmoney.com/",
                    "Accept": "application/json, text/plain, */*"
                },
                "symbol_mapping": {
                    "USDCNY": "133.USDCNH",
                    "EURCNY": "133.EURCNH"
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
        }


def validate_config_json(config_json: str) -> tuple[bool, str, Optional[dict]]:
    """
    验证配置文件JSON是否有效。

    Args:
        config_json: 配置JSON字符串

    Returns:
        (是否有效, 错误消息, 解析后的配置dict)
    """
    import json

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
    import json

    config = {
        "version": "1.0",
        "name": "东方财富外汇数据源",
        "type": "akshare",
        "market": "forex",
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
            "AUDJPY": "133.AUDJPY",
            "USDSGD": "133.USDSGD",
            "USDHKD": "133.USDHKD"
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