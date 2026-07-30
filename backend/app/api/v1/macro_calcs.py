"""指标测算 API."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.macro_calc import RuleResponse, CalcResultResponse, RuleUpdateConfig
from app.services.macro_calc_service import MacroCalcService

router = APIRouter(prefix="/macro/calc", tags=["指标测算"])


@router.get("/rules", response_model=dict)
async def list_rules(db: AsyncSession = Depends(get_db)):
    """获取所有启用的规则."""
    svc = MacroCalcService(db)
    rows = await svc.list_rules()
    data = [dict(r._mapping) for r in rows]
    for d in data:
        d["id"] = str(d["id"])
        d["created_at"] = str(d["created_at"]) if d.get("created_at") else None
        d["updated_at"] = str(d["updated_at"]) if d.get("updated_at") else None
    return {"success": True, "data": data}


@router.get("/rules/{rule_code}", response_model=dict)
async def get_rule(rule_code: str, db: AsyncSession = Depends(get_db)):
    """获取规则详情."""
    svc = MacroCalcService(db)
    row = await svc.get_rule(rule_code)
    if not row:
        raise HTTPException(404, "规则不存在")
    d = dict(row._mapping)
    d["id"] = str(d["id"])
    d["created_at"] = str(d["created_at"]) if d.get("created_at") else None
    d["updated_at"] = str(d["updated_at"]) if d.get("updated_at") else None
    return {"success": True, "data": d}


@router.put("/rules/{rule_code}/config", response_model=dict)
async def update_rule_config(rule_code: str, body: RuleUpdateConfig, db: AsyncSession = Depends(get_db)):
    """更新规则配置."""
    svc = MacroCalcService(db)
    await svc.update_rule_config(
        rule_code,
        body.variables_config.model_dump() if body.variables_config else None,
        body.constants_config.model_dump() if body.constants_config else None
    )
    return {"success": True, "message": "配置已更新"}


@router.post("/execute/{rule_code}", response_model=dict)
async def execute_calc(rule_code: str, db: AsyncSession = Depends(get_db)):
    """执行测算."""
    svc = MacroCalcService(db)
    try:
        result = await svc.execute_rule(rule_code)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/results", response_model=dict)
async def get_results(
    rule_code: Optional[str] = Query(None),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """查询测算历史."""
    svc = MacroCalcService(db)
    rows = await svc.get_results(rule_code, limit)
    data = []
    for r in rows:
        d = dict(r._mapping)
        d["id"] = str(d["id"])
        d["rule_id"] = str(d["rule_id"])
        d["result_value"] = float(d["result_value"]) if d["result_value"] else None
        d["result_period"] = str(d["result_period"]) if d.get("result_period") else None
        d["created_at"] = str(d["created_at"]) if d.get("created_at") else None
        data.append(d)
    return {"success": True, "data": data}
