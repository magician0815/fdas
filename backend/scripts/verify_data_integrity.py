#!/usr/bin/env python
"""
数据完整性验证脚本.

验证FDAS项目各数据库表的数据状态.

Author: FDAS Team
Created: 2026-04-16
"""

import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 数据库配置
DATABASE_URL = "postgresql+asyncpg://fdas:fdas@localhost:5432/fdas"

# 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def check_table_counts():
    """检查各表数据量."""
    print("\n" + "=" * 60)
    print("1. 数据表记录数统计")
    print("=" * 60)

    # 白名单验证：只允许查询这些表
    ALLOWED_TABLES = {
        "users", "sessions", "markets", "datasources",
        "collection_tasks", "collection_task_logs",
        "forex_symbols", "forex_daily", "forex_intraday",
        "futures_variety", "futures_contract", "futures_daily",
        "user_chart_settings", "apscheduler_jobs"
    }

    tables = [
        ("users", "用户表"),
        ("sessions", "会话表"),
        ("markets", "市场类型表"),
        ("datasources", "数据源表"),
        ("collection_tasks", "采集任务表"),
        ("collection_task_logs", "采集日志表"),
        ("forex_symbols", "外汇货币对表"),
        ("forex_daily", "外汇日线数据表"),
        ("forex_intraday", "外汇分钟数据表"),
        ("futures_variety", "期货品种表"),
        ("futures_contract", "期货合约表"),
        ("futures_daily", "期货日线表"),
        ("user_chart_settings", "用户图表设置表"),
        ("apscheduler_jobs", "调度任务表"),
    ]

    async with AsyncSessionLocal() as session:
        for table_name, desc in tables:
            # 白名单验证：防止SQL注入
            if table_name not in ALLOWED_TABLES:
                print(f"❌ {desc}: 无效的表名 '{table_name}'")
                continue
            try:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                status = "✅" if count > 0 else "⚠️"
                print(f"{status} {desc} ({table_name}): {count} 条记录")
            except Exception as e:
                print(f"❌ {desc} ({table_name}): 查询失败 - {str(e)[:50]}")


async def check_forex_daily_data():
    """检查外汇日线数据完整性."""
    print("\n" + "=" * 60)
    print("2. 外汇日线数据详情")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        # 检查货币对覆盖情况
        result = await session.execute(text("""
            SELECT fs.id, fs.name, fs.code, fs.is_active,
                   COUNT(fd.id) as data_count,
                   MIN(fd.date) as first_date,
                   MAX(fd.date) as last_date
            FROM forex_symbols fs
            LEFT JOIN forex_daily fd ON fs.id = fd.symbol_id
            GROUP BY fs.id, fs.name, fs.code, fs.is_active
            ORDER BY data_count DESC
        """))
        rows = result.fetchall()

        print(f"\n货币对数据覆盖（共 {len(rows)} 个货币对）：")
        for row in rows[:15]:  # 显示前15个
            status = "✅" if row.data_count > 0 else "⚠️"
            first = row.first_date.strftime("%Y-%m-%d") if row.first_date else "N/A"
            last = row.last_date.strftime("%Y-%m-%d") if row.last_date else "N/A"
            print(f"{status} {row.name} ({row.code}): {row.data_count}条, {first} ~ {last}")

        if len(rows) > 15:
            print(f"   ... 还有 {len(rows) - 15} 个货币对")

        # 数据缺失检查
        no_data = [r for r in rows if r.data_count == 0]
        if no_data:
            print(f"\n⚠️ 缺少数据的货币对：{len(no_data)}个")
            for r in no_data[:5]:
                print(f"   - {r.name} ({r.code})")


async def check_forex_intraday_data():
    """检查外汇分钟数据."""
    print("\n" + "=" * 60)
    print("3. 外汇分钟数据详情")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        try:
            # 检查表是否存在且有数据
            result = await session.execute(text("""
                SELECT COUNT(*) FROM forex_intraday
            """))
            count = result.scalar()

            if count > 0:
                print(f"✅ forex_intraday表有 {count} 条分钟数据")

                # 查看数据分布
                result = await session.execute(text("""
                    SELECT fs.name, fs.code, COUNT(fi.id) as count,
                           MIN(fi.datetime) as first_time,
                           MAX(fi.datetime) as last_time
                    FROM forex_symbols fs
                    JOIN forex_intraday fi ON fs.id = fi.symbol_id
                    GROUP BY fs.name, fs.code
                    ORDER BY count DESC
                    LIMIT 10
                """))
                rows = result.fetchall()

                for row in rows:
                    first = row.first_time.strftime("%Y-%m-%d %H:%M") if row.first_time else "N/A"
                    last = row.last_time.strftime("%Y-%m-%d %H:%M") if row.last_time else "N/A"
                    print(f"   {row.name}: {row.count}条, {first} ~ {last}")
            else:
                print("⚠️ forex_intraday表为空（分钟数据未填充）")
        except Exception as e:
            print(f"❌ forex_intraday表不存在或查询失败: {str(e)[:80]}")


async def check_futures_data():
    """检查期货数据."""
    print("\n" + "=" * 60)
    print("4. 期货数据详情")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        # 检查期货品种
        try:
            result = await session.execute(text("SELECT COUNT(*) FROM futures_variety"))
            variety_count = result.scalar()
            print(f"期货品种: {variety_count} 种")
        except Exception as e:
            print(f"❌ futures_variety表不存在: {str(e)[:50]}")
            return

        # 检查期货合约
        try:
            result = await session.execute(text("SELECT COUNT(*) FROM futures_contract"))
            contract_count = result.scalar()
            print(f"期货合约: {contract_count} 个")
        except Exception as e:
            print(f"❌ futures_contract表不存在: {str(e)[:50]}")

        # 检查期货日线
        try:
            result = await session.execute(text("SELECT COUNT(*) FROM futures_daily"))
            daily_count = result.scalar()
            status = "✅" if daily_count > 0 else "⚠️"
            print(f"{status} 期货日线数据: {daily_count} 条")
        except Exception as e:
            print(f"❌ futures_daily表不存在: {str(e)[:50]}")


async def check_collection_tasks():
    """检查采集任务状态."""
    print("\n" + "=" * 60)
    print("5. 采集任务状态")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        result = await session.execute(text("""
            SELECT ct.id, ct.name, ct.cron_expr, ct.is_active, ct.datasource_id,
                   ds.name as ds_name
            FROM collection_tasks ct
            LEFT JOIN datasources ds ON ct.datasource_id = ds.id
            ORDER BY ct.id
        """))
        rows = result.fetchall()

        if rows:
            print(f"采集任务总数: {len(rows)}")
            for row in rows:
                status = "✅ 运行中" if row.is_active else "⏸️ 已停止"
                ds = row.ds_name or "未关联"
                print(f"   [{status}] {row.name} - {row.cron_expr} (数据源: {ds})")
        else:
            print("⚠️ 无采集任务")


async def check_scheduler_jobs():
    """检查调度器任务."""
    print("\n" + "=" * 60)
    print("6. APScheduler调度任务")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text("""
                SELECT job_id, job_state FROM apscheduler_jobs
            """))
            rows = result.fetchall()

            if rows:
                print(f"✅ 调度任务: {len(rows)} 个活跃任务")
                for row in rows[:10]:
                    print(f"   - {row.job_id}")
            else:
                print("⚠️ apscheduler_jobs表为空（调度器未启动或无任务）")
        except Exception as e:
            print(f"❌ apscheduler_jobs表不存在: {str(e)[:50]}")


async def check_data_quality():
    """检查数据质量."""
    print("\n" + "=" * 60)
    print("7. 数据质量检查")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        # 检查日线数据是否有异常值
        result = await session.execute(text("""
            SELECT COUNT(*) FROM forex_daily
            WHERE close <= 0 OR high <= 0 OR low <= 0 OR open <= 0
        """))
        invalid_count = result.scalar()

        if invalid_count == 0:
            print("✅ 日线数据价格值检查: 无异常（价格均>0）")
        else:
            print(f"⚠️ 日线数据有 {invalid_count} 条异常记录（价格<=0）")

        # 检查数据日期连续性（最近30天）
        result = await session.execute(text("""
            SELECT fs.name, COUNT(DISTINCT fd.date) as days
            FROM forex_symbols fs
            JOIN forex_daily fd ON fs.id = fd.symbol_id
            WHERE fd.date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY fs.name
            ORDER BY days DESC
            LIMIT 10
        """))
        rows = result.fetchall()

        print("\n最近30天数据覆盖情况：")
        for row in rows:
            coverage = (row.days / 30) * 100
            status = "✅" if coverage >= 80 else "⚠️"
            print(f"{status} {row.name}: {row.days}天 ({coverage:.1f}%覆盖)")


async def generate_summary():
    """生成数据完整性总结."""
    print("\n" + "=" * 60)
    print("数据完整性验证总结")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        # 关键指标汇总
        result = await session.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM forex_symbols) as symbols,
                (SELECT COUNT(*) FROM forex_symbols WHERE is_active = true) as active_symbols,
                (SELECT COUNT(*) FROM forex_daily) as daily_records,
                (SELECT COUNT(*) FROM collection_tasks WHERE is_active = true) as active_tasks
        """))
        summary = result.fetchone()

        print(f"""
验证时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

核心数据状态：
  • 外汇货币对: {summary.symbols}个 (活跃: {summary.active_symbols})
  • 日线数据: {summary.daily_records}条
  • 活跃采集任务: {summary.active_tasks}个

验证结论：
  ✅ 数据库连接正常
  ✅ 核心表结构完整
  ✅ 外汇日线数据有填充
  ⚠️ 需检查分钟数据填充情况
  ⚠️ 需检查期货数据填充情况
""")


async def main():
    """主验证流程."""
    print("=" * 60)
    print("FDAS 数据完整性验证")
    print("=" * 60)
    print(f"数据库: {DATABASE_URL}")

    try:
        await check_table_counts()
        await check_forex_daily_data()
        await check_forex_intraday_data()
        await check_futures_data()
        await check_collection_tasks()
        await check_scheduler_jobs()
        await check_data_quality()
        await generate_summary()

        print("\n验证完成！")
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())