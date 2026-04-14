"""
股票市场识别工具.

提供股票市场类型识别、涨跌停阈值判断等功能.

Author: FDAS Team
Created: 2026-04-14
"""

import re
from typing import Optional


def identify_market_type(symbol_code: str, symbol_name: Optional[str] = None) -> str:
    """根据品种代码识别市场类型.

    Args:
        symbol_code: 品种代码（如 '600000', '300001', '688001'）
        symbol_name: 品种名称（可选，用于ST股票判断）

    Returns:
        市场类型字符串
    """
    if not symbol_code:
        return "forex"

    # 清理代码（去除前后缀）
    clean_code = symbol_code.upper().replace(" ", "")

    # 外汇判断：通常为6位字母组合如 EURUSD, USDCNY
    if re.match(r"^[A-Z]{6}$", clean_code):
        return "forex"

    # 科创板：688开头
    if re.match(r"^688\d{3}$", clean_code):
        return "stock_kcb"

    # 创业板：300开头
    if re.match(r"^300\d{3}$", clean_code):
        return "stock_cyb"

    # 北交所：8开头或4开头（老三板转板）
    if re.match(r"^(8|4)\d{5}$", clean_code):
        return "stock_bjb"

    # ST股票判断：名称包含ST
    if symbol_name and "ST" in symbol_name.upper():
        return "stock_st"

    # A股普通股票：6开头（沪市）或0开头（深市）
    if re.match(r"^6\d{5}$", clean_code) or re.match(r"^0\d{5}$", clean_code):
        return "stock_a"

    # 默认返回外汇
    return "forex"


def get_market_config(market_type: str) -> dict:
    """获取市场配置信息.

    Args:
        market_type: 市场类型

    Returns:
        市场配置字典
    """
    configs = {
        "forex": {
            "name": "外汇",
            "limit_up_threshold": 0,
            "limit_down_threshold": 0,
            "price_precision": 4,
            "has_limit": False,
            "need_adjustment": False,
            "is_24h_trading": True
        },
        "stock_a": {
            "name": "A股",
            "limit_up_threshold": 10,
            "limit_down_threshold": 10,
            "price_precision": 2,
            "has_limit": True,
            "need_adjustment": True,
            "is_24h_trading": False
        },
        "stock_kcb": {
            "name": "科创板",
            "limit_up_threshold": 20,
            "limit_down_threshold": 20,
            "price_precision": 2,
            "has_limit": True,
            "need_adjustment": True,
            "is_24h_trading": False
        },
        "stock_cyb": {
            "name": "创业板",
            "limit_up_threshold": 20,
            "limit_down_threshold": 20,
            "price_precision": 2,
            "has_limit": True,
            "need_adjustment": True,
            "is_24h_trading": False
        },
        "stock_st": {
            "name": "ST股",
            "limit_up_threshold": 5,
            "limit_down_threshold": 5,
            "price_precision": 2,
            "has_limit": True,
            "need_adjustment": True,
            "is_24h_trading": False
        },
        "stock_bjb": {
            "name": "北交所",
            "limit_up_threshold": 30,
            "limit_down_threshold": 30,
            "price_precision": 2,
            "has_limit": True,
            "need_adjustment": True,
            "is_24h_trading": False
        }
    }

    return configs.get(market_type, configs["forex"])


def calculate_limit_price(prev_close: float, market_type: str, direction: str) -> float:
    """计算涨跌停价格.

    Args:
        prev_close: 昨日收盘价
        market_type: 市场类型
        direction: up（涨停）/down（跌停）

    Returns:
        涨跌停价格
    """
    config = get_market_config(market_type)

    if not config["has_limit"]:
        return 0

    threshold = config.get(f"limit_{direction}_threshold", 0)
    precision = config.get("price_precision", 2)

    if direction == "up":
        price = prev_close * (1 + threshold / 100)
    else:
        price = prev_close * (1 - threshold / 100)

    # 按精度取整
    multiplier = 10 ** precision
    return round(price * multiplier) / multiplier


def is_limit_price(current_price: float, limit_price: float, market_type: str) -> bool:
    """判断是否达到涨跌停.

    Args:
        current_price: 当前价格
        limit_price: 涨跌停价格
        market_type: 市场类型

    Returns:
        是否涨跌停
    """
    config = get_market_config(market_type)

    if not config["has_limit"]:
        return False

    # 允许0.01%的误差（由于价格精度限制）
    tolerance = 0.0001

    return abs(current_price - limit_price) <= tolerance * limit_price