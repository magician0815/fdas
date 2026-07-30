"""测算引擎 Pydantic Schema."""

from typing import Optional
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field


# ========== 规则 ==========

class VariableConfigItem(BaseModel):
    label: str
    description: str = ""
    sources: Optional[list[str]] = None
    priority: Optional[list[str]] = None
    current_binding: Optional[str] = None
    type: Optional[str] = None  # "constant" for constants
    default_value: Optional[float] = None
    transform: Optional[str] = None
    frequency: Optional[str] = None


class ConstantConfigItem(BaseModel):
    label: str
    value: float
    description: str = ""


class RuleResponse(BaseModel):
    id: UUID
    rule_code: str
    rule_name: str
    description: Optional[str]
    formula_latex: str
    variables_config: dict
    constants_config: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class RuleUpdateConfig(BaseModel):
    variables_config: Optional[dict] = None
    constants_config: Optional[dict] = None


# ========== 计算结果 ==========

class CalcResultResponse(BaseModel):
    id: UUID
    rule_id: UUID
    rule_code: str
    result_value: Optional[float]
    result_period: Optional[date]
    variable_snapshot: dict
    calculation_process: dict
    rule_snapshot: dict
    created_at: datetime
    model_config = {"from_attributes": True}


class CalcExecuteResponse(BaseModel):
    success: bool
    rule_code: str
    result_value: float
    result_period: str
    variable_snapshot: dict
    calculation_process: dict
    rule_snapshot: dict
