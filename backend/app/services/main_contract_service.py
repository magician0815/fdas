"""
主力合约拼接服务.

实现期货主力连续合约的拼接逻辑，自动识别主力合约切换点，
将不同月份合约数据拼接成连续的价格序列.

主力合约识别规则：
- 根据持仓量(Open Interest)判断当前主力合约
- 持仓量最大的合约为当前主力合约
- 主力合约切换时进行挢月平滑处理

Author: FDAS Team
Created: 2026-04-14
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, timedelta
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class MainContractService:
    """主力合约拼接服务类."""

    # 主力合约切换的持仓量阈值比例
    OI_SWITCH_THRESHOLD = 0.7  # 当新合约OI超过旧合约70%时认为即将切换

    def identify_main_contract(
        self,
        contracts_data: List[Dict[str, Any]],
        target_date: date
    ) -> Optional[str]:
        """
        识别指定日期的主力合约.

        根据持仓量判断哪个合约是当天的主力合约.

        Args:
            contracts_data: 各合约的日线数据列表，每项包含contract_id, date, open_interest等
            target_date: 目标日期

        Returns:
            主力合约ID，如果无法识别则返回None
        """
        # 获取目标日期所有合约的数据
        date_data = [d for d in contracts_data if d.get("date") == target_date]

        if not date_data:
            return None

        # 按持仓量排序，取最大
        sorted_data = sorted(
            date_data,
            key=lambda x: x.get("open_interest", 0) or 0,
            reverse=True
        )

        main_contract = sorted_data[0]
        oi = main_contract.get("open_interest", 0)

        # 持仓量为0的合约不作为主力
        if oi == 0:
            logger.warning(f"日期 {target_date} 所有合约持仓量为0")
            return None

        return main_contract.get("contract_id")

    def detect_contract_switches(
        self,
        contracts_data: List[Dict[str, Any]],
        variety_code: str
    ) -> List[Dict[str, Any]]:
        """
        检测主力合约切换点.

        遍历历史数据，找出主力合约从旧合约切换到新合约的时间点.

        Args:
            contracts_data: 各合约的日线数据列表
            variety_code: 品种代码

        Returns:
            切换点列表，每项包含:
            {
                "switch_date": 切换日期,
                "old_contract_id": 旧主力合约ID,
                "old_contract_code": 旧主力合约代码,
                "new_contract_id": 新主力合约ID,
                "new_contract_code": 新主力合约代码,
                "old_close": 旧合约收盘价,
                "new_close": 新合约收盘价,
                "price_diff": 价格差,
                "adjust_ratio": 调整比例
            }
        """
        if not contracts_data:
            return []

        # 按日期排序
        sorted_data = sorted(contracts_data, key=lambda x: x.get("date"))

        switches = []
        current_main_id = None
        prev_date = None

        for data in sorted_data:
            current_date = data.get("date")
            current_contract_id = data.get("contract_id")
            oi = data.get("open_interest", 0) or 0

            # 第一天初始化
            if current_main_id is None:
                current_main_id = self.identify_main_contract(contracts_data, current_date)
                prev_date = current_date
                continue

            # 检查是否发生切换
            new_main_id = self.identify_main_contract(contracts_data, current_date)

            if new_main_id and new_main_id != current_main_id:
                # 找到切换点，记录切换信息
                old_contract_data = [d for d in sorted_data
                                     if d.get("date") == prev_date
                                     and d.get("contract_id") == current_main_id]
                new_contract_data = [d for d in sorted_data
                                     if d.get("date") == current_date
                                     and d.get("contract_id") == new_main_id]

                if old_contract_data and new_contract_data:
                    old_close = old_contract_data[0].get("close")
                    new_close = new_contract_data[0].get("close")

                    # 计算价格差和调整比例
                    price_diff = 0
                    adjust_ratio = 1.0

                    if old_close and new_close and old_close != 0:
                        price_diff = float(new_close) - float(old_close)
                        adjust_ratio = float(old_close) / float(new_close)

                    switch_info = {
                        "switch_date": current_date,
                        "old_contract_id": current_main_id,
                        "old_contract_code": old_contract_data[0].get("contract_code"),
                        "new_contract_id": new_main_id,
                        "new_contract_code": new_contract_data[0].get("contract_code"),
                        "old_close": float(old_close) if old_close else None,
                        "new_close": float(new_close) if new_close else None,
                        "price_diff": price_diff,
                        "adjust_ratio": adjust_ratio,
                        "variety_code": variety_code
                    }

                    switches.append(switch_info)
                    logger.info(f"品种 {variety_code} 在 {current_date} 发生主力合约切换: "
                               f"{old_contract_data[0].get('contract_code')} → {new_contract_data[0].get('contract_code')}")

                # 更新当前主力合约
                current_main_id = new_main_id

            prev_date = current_date

        return switches

    def build_main_continuous_series(
        self,
        contracts_data: List[Dict[str, Any]],
        switches: List[Dict[str, Any]],
        smooth_method: str = "price_adjust"
    ) -> List[Dict[str, Any]]:
        """
        构建主力连续合约序列.

        将不同月份的主力合约数据拼接成连续序列，
        根据平滑方法处理挢月价格跳空.

        Args:
            contracts_data: 各合约的日线数据列表
            switches: 主力合约切换点列表
            smooth_method: 平滑方法
                - "price_adjust": 价格调整法（向后调整历史价格）
                - "forward_adjust": 向前调整（调整后续价格）
                - "none": 不调整，保留原始价格

        Returns:
            主力连续合约数据列表
        """
        if not contracts_data:
            return []

        # 按日期排序
        sorted_data = sorted(contracts_data, key=lambda x: x.get("date"))

        # 标记主力合约数据
        main_data = []
        current_adjust_ratio = 1.0  # 当前累计调整比例

        # 构建切换日期映射
        switch_map = {s["switch_date"]: s for s in switches}

        for data in sorted_data:
            current_date = data.get("date")

            # 检查是否是主力合约数据（持仓量最大）
            main_contract_id = self.identify_main_contract(contracts_data, current_date)

            if data.get("contract_id") == main_contract_id:
                # 这是主力合约数据
                adjusted_data = data.copy()
                adjusted_data["is_main_data"] = True

                # 检查是否发生切换
                if current_date in switch_map:
                    switch = switch_map[current_date]

                    if smooth_method == "price_adjust":
                        # 后向调整：调整历史数据价格，累计调整比例
                        current_adjust_ratio *= switch["adjust_ratio"]
                    elif smooth_method == "forward_adjust":
                        # 前向调整：不累计，只调整切换后数据
                        current_adjust_ratio = switch["adjust_ratio"]
                    else:
                        # 不调整
                        current_adjust_ratio = 1.0

                # 应用调整
                if smooth_method != "none" and current_adjust_ratio != 1.0:
                    if adjusted_data.get("open"):
                        adjusted_data["adjusted_price"] = float(adjusted_data["open"]) * current_adjust_ratio
                        adjusted_data["adjusted_open"] = float(adjusted_data["open"]) * current_adjust_ratio
                    if adjusted_data.get("high"):
                        adjusted_data["adjusted_high"] = float(adjusted_data["high"]) * current_adjust_ratio
                    if adjusted_data.get("low"):
                        adjusted_data["adjusted_low"] = float(adjusted_data["low"]) * current_adjust_ratio
                    if adjusted_data.get("close"):
                        adjusted_data["adjusted_close"] = float(adjusted_data["close"]) * current_adjust_ratio

                adjusted_data["adjust_ratio"] = current_adjust_ratio
                main_data.append(adjusted_data)

        return main_data

    def calculate_spread_adjustment(
        self,
        old_close: float,
        new_close: float,
        method: str = "proportional"
    ) -> float:
        """
        计算挢月价格调整比例.

        Args:
            old_close: 旧合约收盘价
            new_close: 新合约收盘价
            method: 调整方法
                - "proportional": 比例调整（调整历史价格）
                - "absolute": 绝对值调整（调整价格差）

        Returns:
            调整比例或调整值
        """
        if old_close == 0 or new_close == 0:
            return 1.0

        if method == "proportional":
            return old_close / new_close
        elif method == "absolute":
            return old_close - new_close
        else:
            return 1.0

    def get_contract_expiry_warning(
        self,
        contracts: List[Dict[str, Any]],
        current_date: date,
        warning_days: int = 5
    ) -> List[Dict[str, Any]]:
        """
        获取即将到期的合约警告.

        Args:
            contracts: 合约列表
            current_date: 当前日期
            warning_days: 提前预警天数

        Returns:
            即将到期的合约列表
        """
        warning_list = []
        warning_date = current_date + timedelta(days=warning_days)

        for contract in contracts:
            last_trade_date = contract.get("last_trade_date")

            if last_trade_date and last_trade_date <= warning_date:
                days_to_expiry = (last_trade_date - current_date).days
                warning_list.append({
                    "contract_id": contract.get("id"),
                    "contract_code": contract.get("contract_code"),
                    "contract_name": contract.get("contract_name"),
                    "last_trade_date": last_trade_date,
                    "days_to_expiry": days_to_expiry,
                    "is_main_contract": contract.get("is_main_contract")
                })

        # 按到期天数排序
        warning_list.sort(key=lambda x: x["days_to_expiry"])

        return warning_list


# 导出服务实例
main_contract_service = MainContractService()