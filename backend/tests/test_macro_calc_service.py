"""指标测算引擎单元测试."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date

from app.services.macro_calc_service import MacroCalcService


class TestOutputGap:
    """产出缺口计算测试."""

    def test_positive_gap(self):
        """正缺口: GDP > 潜在."""
        result = MacroCalcService._compute_output_gap(23000, 22780)
        assert result == 0.97  # ≈ (23000-22780)/22780*100

    def test_negative_gap(self):
        """负缺口: GDP < 潜在."""
        result = MacroCalcService._compute_output_gap(22000, 22780)
        assert result == -3.42

    def test_zero_gap(self):
        """零缺口."""
        assert MacroCalcService._compute_output_gap(22780, 22780) == 0.0

    def test_zero_potential(self):
        """潜在GDP为零时返回0."""
        assert MacroCalcService._compute_output_gap(23000, 0) == 0.0

    def test_precision(self):
        """精度: 保留两位小数."""
        result = MacroCalcService._compute_output_gap(24180.419, 23945.1378387)
        assert result == 0.98


class TestQuarterEnd:
    """季度末日期测试."""

    def test_q1(self):
        assert str(MacroCalcService._quarter_end(3, 2026)) == "2026-03-01"

    def test_q2(self):
        assert str(MacroCalcService._quarter_end(6, 2026)) == "2026-06-01"

    def test_q3(self):
        assert str(MacroCalcService._quarter_end(9, 2026)) == "2026-09-01"


class TestExecuteRule:
    """完整测算流程测试."""

    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        return db

    @pytest.fixture
    def svc(self, mock_db):
        return MacroCalcService(mock_db)

    async def test_execute_success(self, svc, mock_db):
        """完整计算流程 — 模拟所有数据可用."""
        # Mock 规则查询
        rule_row = MagicMock()
        rule_row._mapping = {
            "id": "rule-id",
            "variables_config": {
                "R_LR_t": {"priority": ["r-sep", "longer-run-neutral"]},
                "PI_t": {},
                "PI_STAR": {"default_value": 2.0},
                "Y_t": {},
                "Y_P_t": {},
            },
            "constants_config": {
                "C_INFLATION": {"value": 0.5},
                "C_OUTPUT": {"value": 1.0},
            },
        }

        call_count = [0]  # mutable for nonlocal access
        async def mock_execute(sql, params=None):
            result = MagicMock()
            call_count[0] += 1
            sc = params.get("sc") if params else None
            if sc == "r-sep":
                row = MagicMock()
                row.__getitem__ = lambda s, i: 3.4 if i == 0 else "2026-06-17"
                result.fetchone.return_value = row
            elif sc == "core_pce":
                pd_val = str(params.get("pd", "")) if params else ""
                if "2026-05" in pd_val:
                    row = MagicMock()
                    row.__getitem__ = lambda s, i: 130.082 if i == 0 else "2026-05-01"
                    result.fetchone.return_value = row
                elif "2025-05" in pd_val:
                    row = MagicMock()
                    row.__getitem__ = lambda s, i: 125.79 if i == 0 else "2025-05-01"
                    result.fetchone.return_value = row
                else:
                    result.fetchone.return_value = None
            elif sc == "real_gdp":
                row = MagicMock()
                row.__getitem__ = lambda s, i: 24180.419 if i == 0 else "2026-01-01"
                result.fetchone.return_value = row
            elif sc == "potential_gdp":
                row = MagicMock()
                row.__getitem__ = lambda s, i: 23945.1378387 if i == 0 else "2026-01-01"
                result.fetchone.return_value = row
            else:
                s = str(sql) if hasattr(sql, 'compile') else sql
                if "macro_calculation_rules" in s:
                    result.fetchone.return_value = rule_row
                else:
                    result.fetchone.return_value = None
            return result

        mock_db.execute = AsyncMock(side_effect=mock_execute)

        result = await svc.execute_rule("BALANCED_APPROACH")
        assert result["success"] is True
        assert result["result_value"] == 8.5  # ≈ 3.4+3.41+0.5*(3.41-2.0)+1.0*0.98
        assert "R_LR_t" in result["variable_snapshot"]
        assert result["variable_snapshot"]["R_LR_t"]["value"] == 3.4

    async def test_rule_not_found(self, svc, mock_db):
        """规则不存在时抛出 ValueError."""
        mock_db.execute = AsyncMock(return_value=MagicMock(fetchone=MagicMock(return_value=None)))
        with pytest.raises(ValueError, match="规则不存在"):
            await svc.execute_rule("UNKNOWN")

    async def test_no_r_lr_data(self, svc, mock_db):
        """r_LR 数据缺失抛出异常."""
        rule_row = MagicMock()
        rule_row._mapping = {
            "id": "rule-id",
            "variables_config": {
                "R_LR_t": {"priority": ["r-sep"]},
                "PI_t": {},
                "PI_STAR": {"default_value": 2.0},
                "Y_t": {},
                "Y_P_t": {},
            },
            "constants_config": {"C_INFLATION": {"value": 0.5}, "C_OUTPUT": {"value": 1.0}},
        }
        mock_db.execute = AsyncMock(return_value=MagicMock(
            fetchone=MagicMock(side_effect=[rule_row, None])
        ))
        with pytest.raises(ValueError, match="无法获取长期自然利率"):
            await svc.execute_rule("BALANCED_APPROACH")


class TestLatestValue:
    """数据查询测试."""

    async def test_get_latest_value(self):
        db = AsyncMock()
        row = MagicMock()
        row.__getitem__ = lambda s, i: 3.4 if i == 0 else "2026-06-17"
        db.execute = AsyncMock(return_value=MagicMock(fetchone=MagicMock(return_value=row)))
        svc = MacroCalcService(db)
        result = await svc._get_latest_value("r-sep")
        assert result["value"] == 3.4
        assert result["period_date"] == "2026-06-17"

    async def test_get_latest_value_not_found(self):
        db = AsyncMock()
        db.execute = AsyncMock(return_value=MagicMock(fetchone=MagicMock(return_value=None)))
        svc = MacroCalcService(db)
        result = await svc._get_latest_value("nonexistent")
        assert result is None


class TestYoY:
    """同比计算测试."""

    async def test_yoy_normal(self):
        db = AsyncMock()
        row_current = MagicMock()
        row_current.__getitem__ = lambda s, i: 130.082 if i == 0 else "2026-05-01"
        row_base = MagicMock()
        row_base.__getitem__ = lambda s, i: 125.79 if i == 0 else "2025-05-01"
        db.execute = AsyncMock(side_effect=[
            MagicMock(fetchone=MagicMock(return_value=row_current)),
            MagicMock(fetchone=MagicMock(return_value=row_base)),
        ])
        svc = MacroCalcService(db)
        result = await svc._compute_yoy(date(2026, 5, 1))
        assert result == 3.41  # (130.082/125.79 - 1) * 100

    async def test_yoy_no_base(self):
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            MagicMock(fetchone=MagicMock(return_value=MagicMock(__getitem__=lambda s,i: 100))),
            MagicMock(fetchone=MagicMock(return_value=None)),  # no base
        ])
        svc = MacroCalcService(db)
        result = await svc._compute_yoy(date(2026, 5, 1))
        assert result is None

    async def test_yoy_no_current(self):
        db = AsyncMock()
        db.execute = AsyncMock(return_value=MagicMock(fetchone=MagicMock(return_value=None)))
        svc = MacroCalcService(db)
        result = await svc._compute_yoy(date(2099, 1, 1))
        assert result is None
