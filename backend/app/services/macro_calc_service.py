"""
宏观指标测算引擎.

基于已存储的宏观数据，执行可配置的金融指标测算规则。
当前内置: 平衡方法规则 (Balanced-Approach Rule).

Author: FDAS Team
Created: 2026-07-30
"""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.macro_calc_rule import MacroCalculationRule
from app.models.macro_calc_result import MacroCalculationResult

logger = logging.getLogger(__name__)


class MacroCalcService:
    """宏观指标测算引擎."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========== 规则管理 ==========

    async def list_rules(self) -> List[MacroCalculationRule]:
        result = await self.db.execute(
            text("SELECT * FROM macro_calculation_rules WHERE is_active = true ORDER BY created_at")
        )
        return result.fetchall()

    async def get_rule(self, rule_code: str):
        result = await self.db.execute(
            text("SELECT * FROM macro_calculation_rules WHERE rule_code = :rc"),
            {"rc": rule_code}
        )
        return result.fetchone()

    async def update_rule_config(self, rule_code: str, variables_config: dict = None, constants_config: dict = None):
        sets = []
        params = {"rc": rule_code}
        if variables_config is not None:
            sets.append("variables_config = :vc")
            params["vc"] = variables_config
        if constants_config is not None:
            sets.append("constants_config = :cc")
            params["cc"] = constants_config
        if not sets:
            return
        await self.db.execute(
            text(f"UPDATE macro_calculation_rules SET {', '.join(sets)}, updated_at = NOW() WHERE rule_code = :rc"),
            params
        )
        await self.db.commit()

    # ========== 数据查询 ==========

    async def _get_latest_value(self, source_code: str, before_date: Optional[date] = None) -> Optional[Dict]:
        """获取某指标最新数据."""
        sql = "SELECT value, period_date FROM macro_data_points WHERE source_code = :sc"
        if before_date:
            sql += " AND period_date <= :bd"
        sql += " ORDER BY period_date DESC LIMIT 1"
        params = {"sc": source_code}
        if before_date:
            params["bd"] = before_date
        result = await self.db.execute(text(sql), params)
        row = result.fetchone()
        if row:
            return {"value": float(row[0]), "period_date": row[1]}
        return None

    async def _get_value_at_period(self, source_code: str, period_month: date) -> Optional[float]:
        """获取某指标指定月份的值(用于 YoY 基期查询)."""
        result = await self.db.execute(
            text("SELECT value FROM macro_data_points WHERE source_code = :sc AND period_date = :pd LIMIT 1"),
            {"sc": source_code, "pd": period_month}
        )
        row = result.fetchone()
        if row and row[0] is not None:
            return float(row[0])
        return None

    # ========== 计算辅助 ==========

    async def _compute_yoy(self, current_month: date) -> Optional[float]:
        """计算 core_pce 同比通胀率: (当月/去年同月 - 1) × 100."""
        current_val = await self._get_value_at_period("core_pce", current_month)
        if current_val is None:
            return None
        base_month = current_month.replace(year=current_month.year - 1)
        base_val = await self._get_value_at_period("core_pce", base_month)
        if base_val is None or base_val == 0:
            return None
        return round((current_val / base_val - 1) * 100, 2)

    @staticmethod
    def _compute_output_gap(gdp: float, potential: float) -> float:
        """产出缺口(比率): (y_t - y_t_P) / y_t_P."""
        if potential == 0:
            return 0.0
        return round((gdp - potential) / potential, 4)

    @staticmethod
    def _quarter_end(month: int, year: int = None) -> date:
        """返回季度末日期."""
        if year is None:
            year = date.today().year
        q = (month - 1) // 3 + 1
        return date(year, q * 3, 1)  # 简化: 返回季度末月1日

    # ========== 主计算流程 ==========

    async def execute_rule(self, rule_code: str) -> Dict[str, Any]:
        """执行完整测算流程."""
        rule = await self.get_rule(rule_code)
        if not rule:
            raise ValueError(f"规则不存在: {rule_code}")

        # 解析配置
        vc = rule._mapping["variables_config"]
        cc = rule._mapping["constants_config"]

        variables = {}
        steps = []

        # 1. r_t_LR: 按 priority 查找
        r_lr_config = vc.get("R_LR_t", {})
        r_lr_val = None
        r_lr_source = None
        r_lr_period = None
        for src in r_lr_config.get("priority", ["r-sep", "longer-run-neutral"]):
            data = await self._get_latest_value(src)
            if data:
                r_lr_val = data["value"]
                r_lr_source = src
                r_lr_period = data["period_date"]
                break
        if r_lr_val is None:
            raise ValueError("无法获取长期自然利率 r_t_LR 的值")
        variables["R_LR_t"] = {"source": r_lr_source, "period": str(r_lr_period), "value": r_lr_val}

        # 2. π_t: core_pce YoY, 从当季末月逐月回退直到找到数据
        pi_config = vc.get("PI_t", {})
        today = date.today()
        qm = ((today.month - 1) // 3) * 3 + 3
        pi_val = None
        pi_period = None
        for offset in range(6):  # 最多回退6个月
            test_month = date(today.year, qm - offset, 1)
            pi_val = await self._compute_yoy(test_month)
            if pi_val is not None:
                pi_period = test_month
                break
        if pi_val is None:
            raise ValueError("无法计算核心PCE同比通胀率")
        variables["PI_t"] = {"source": "core_pce", "period": str(pi_period), "value": pi_val}

        # 3. π*: 目标通胀率
        pi_star_config = vc.get("PI_STAR", {})
        pi_star = pi_star_config.get("default_value", 2.0)
        variables["PI_STAR"] = {"source": "constant", "period": None, "value": pi_star}

        # 4. y_t + y_t_P (取同一季度, 以 real_gdp 的期间为准)
        gdp = await self._get_latest_value("real_gdp")
        if not gdp:
            raise ValueError("无法获取实际GDP数据")
        # 取相同期间或最接近的潜在GDP
        gdp_period = gdp["period_date"]
        potential = await self._get_latest_value("potential_gdp", gdp_period)
        if not potential:
            raise ValueError("无法获取潜在GDP数据")

        y_val = gdp["value"]
        yp_val = potential["value"]
        variables["Y_t"] = {"source": "real_gdp", "period": str(gdp["period_date"]), "value": y_val}
        variables["Y_P_t"] = {"source": "potential_gdp", "period": str(potential["period_date"]), "value": yp_val}

        # 5. 产出缺口 (比率, 在公式中 ×100% 等同于 ×1)
        output_gap = self._compute_output_gap(y_val, yp_val)
        gap_pct = round(output_gap * 100, 2)
        steps.append({
            "step": 1,
            "description": "产出缺口",
            "formula": f"({y_val} - {yp_val}) / {yp_val} × 100%",
            "result": f"{gap_pct}%"
        })

        # 6. 系数
        c_inflation = cc.get("C_INFLATION", {}).get("value", 0.5)
        c_output = cc.get("C_OUTPUT", {}).get("value", 1.0)

        # 7. 主公式
        ffr = r_lr_val + pi_val + c_inflation * (pi_val - pi_star) + c_output * output_gap
        ffr = round(ffr, 2)

        main_formula = f"{r_lr_val} + {pi_val} + {c_inflation}×({pi_val}-{pi_star}) + {c_output}×{output_gap}"
        steps.append({
            "step": 2,
            "description": "代入主公式",
            "formula": main_formula,
            "result": ffr
        })

        # 8. 结果期间(取季度末)
        def _to_date(v):
            if isinstance(v, date): return v
            try: return date.fromisoformat(str(v)[:10])
            except: return date.today()
        periods = [_to_date(pi_period), _to_date(gdp["period_date"]), _to_date(r_lr_period)]
        result_period = max(periods) if periods else date.today()

        # 9. 保存结果
        rule_snapshot = {"variables_config": vc, "constants_config": cc}
        result = MacroCalculationResult(
            rule_id=rule._mapping["id"],
            rule_code=rule_code,
            result_value=ffr,
            result_period=result_period,
            variable_snapshot=variables,
            calculation_process={"steps": steps, "final_result": ffr},
            rule_snapshot=rule_snapshot,
        )
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)

        return {
            "success": True,
            "rule_code": rule_code,
            "result_value": ffr,
            "result_period": str(result_period),
            "variable_snapshot": variables,
            "calculation_process": {"steps": steps, "final_result": ffr},
            "rule_snapshot": rule_snapshot,
        }

    async def get_results(self, rule_code: str = None, limit: int = 10):
        sql = "SELECT * FROM macro_calculation_results"
        params = {}
        if rule_code:
            sql += " WHERE rule_code = :rc"
            params["rc"] = rule_code
        sql += " ORDER BY created_at DESC LIMIT :lim"
        params["lim"] = limit
        result = await self.db.execute(text(sql), params)
        return result.fetchall()
