-- FDAS 数据库初始化脚本
-- 金融数据抓取与分析系统
-- Author: FDAS Team
-- Created: 2026-04-03
-- Updated: 2026-04-10 - 按市场分表设计，新增markets、forex_symbols、forex_daily表

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 业务系统表
-- ============================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE users IS '用户账户信息表';
COMMENT ON COLUMN users.id IS '用户唯一标识ID';
COMMENT ON COLUMN users.username IS '用户名';
COMMENT ON COLUMN users.password_hash IS '密码哈希值';
COMMENT ON COLUMN users.role IS '用户角色';
COMMENT ON COLUMN users.created_at IS '创建时间';
COMMENT ON COLUMN users.updated_at IS '更新时间';

-- Session表（服务端Session存储）
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

COMMENT ON TABLE sessions IS '用户登录会话信息表';
COMMENT ON COLUMN sessions.id IS '会话唯一标识ID';
COMMENT ON COLUMN sessions.user_id IS '关联用户ID';
COMMENT ON COLUMN sessions.session_data IS '会话数据';
COMMENT ON COLUMN sessions.created_at IS '创建时间';
COMMENT ON COLUMN sessions.expires_at IS '过期时间';

-- 市场类型定义表
CREATE TABLE IF NOT EXISTS markets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE markets IS '市场类型定义表';
COMMENT ON COLUMN markets.id IS '市场唯一标识ID';
COMMENT ON COLUMN markets.code IS '市场代码';
COMMENT ON COLUMN markets.name IS '市场名称';
COMMENT ON COLUMN markets.description IS '市场描述说明';
COMMENT ON COLUMN markets.timezone IS '市场交易时区';
COMMENT ON COLUMN markets.is_active IS '是否启用';
COMMENT ON COLUMN markets.created_at IS '创建时间';
COMMENT ON COLUMN markets.updated_at IS '更新时间';

-- 数据源配置表
CREATE TABLE IF NOT EXISTS datasources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    market_id UUID REFERENCES markets(id),
    interface VARCHAR(50) NOT NULL,
    description TEXT,
    config_schema JSONB NOT NULL,
    supported_symbols JSONB,
    min_date DATE,
    type VARCHAR(50) NOT NULL DEFAULT 'akshare',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE datasources IS '数据源配置信息表';
COMMENT ON COLUMN datasources.id IS '数据源唯一标识ID';
COMMENT ON COLUMN datasources.name IS '数据源名称';
COMMENT ON COLUMN datasources.market_id IS '适用市场类型ID';
COMMENT ON COLUMN datasources.interface IS 'AKShare接口名称';
COMMENT ON COLUMN datasources.description IS '数据源描述说明';
COMMENT ON COLUMN datasources.config_schema IS '配置参数Schema';
COMMENT ON COLUMN datasources.supported_symbols IS '支持的货币对列表';
COMMENT ON COLUMN datasources.min_date IS '接口最早可用数据日期';
COMMENT ON COLUMN datasources.type IS '数据源类型';
COMMENT ON COLUMN datasources.is_active IS '是否启用';
COMMENT ON COLUMN datasources.created_at IS '创建时间';
COMMENT ON COLUMN datasources.updated_at IS '更新时间';

-- 采集任务表
CREATE TABLE IF NOT EXISTS collection_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    datasource_id UUID NOT NULL REFERENCES datasources(id) ON DELETE CASCADE,
    market_id UUID NOT NULL REFERENCES markets(id),
    symbol_id UUID NOT NULL,
    start_date DATE,
    end_date DATE,
    cron_expr VARCHAR(100),
    is_enabled BOOLEAN DEFAULT false,
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    last_status VARCHAR(20),
    last_message TEXT,
    last_records_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE collection_tasks IS '采集任务配置和执行状态表';
COMMENT ON COLUMN collection_tasks.id IS '任务唯一标识ID';
COMMENT ON COLUMN collection_tasks.name IS '任务名称';
COMMENT ON COLUMN collection_tasks.datasource_id IS '关联数据源ID';
COMMENT ON COLUMN collection_tasks.market_id IS '目标市场类型ID';
COMMENT ON COLUMN collection_tasks.symbol_id IS '目标标的ID';
COMMENT ON COLUMN collection_tasks.start_date IS '采集开始日期';
COMMENT ON COLUMN collection_tasks.end_date IS '采集结束日期';
COMMENT ON COLUMN collection_tasks.cron_expr IS 'Cron定时表达式';
COMMENT ON COLUMN collection_tasks.is_enabled IS '是否启用';
COMMENT ON COLUMN collection_tasks.last_run_at IS '上次执行时间';
COMMENT ON COLUMN collection_tasks.next_run_at IS '下次执行时间';
COMMENT ON COLUMN collection_tasks.last_status IS '上次执行状态';
COMMENT ON COLUMN collection_tasks.last_message IS '上次执行消息';
COMMENT ON COLUMN collection_tasks.last_records_count IS '上次采集记录数';
COMMENT ON COLUMN collection_tasks.created_at IS '创建时间';
COMMENT ON COLUMN collection_tasks.updated_at IS '更新时间';

-- 采集任务执行日志表
CREATE TABLE IF NOT EXISTS collection_task_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES collection_tasks(id) ON DELETE CASCADE,
    run_at TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL,
    records_count INTEGER DEFAULT 0,
    message TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE collection_task_logs IS '采集任务执行日志表';
COMMENT ON COLUMN collection_task_logs.id IS '日志唯一标识ID';
COMMENT ON COLUMN collection_task_logs.task_id IS '关联任务ID';
COMMENT ON COLUMN collection_task_logs.run_at IS '执行时间';
COMMENT ON COLUMN collection_task_logs.status IS '执行状态';
COMMENT ON COLUMN collection_task_logs.records_count IS '采集记录数';
COMMENT ON COLUMN collection_task_logs.message IS '执行消息或错误信息';
COMMENT ON COLUMN collection_task_logs.duration_ms IS '执行耗时（毫秒）';
COMMENT ON COLUMN collection_task_logs.created_at IS '创建时间';

-- APScheduler任务表
CREATE TABLE IF NOT EXISTS apscheduler_jobs (
    id VARCHAR(255) PRIMARY KEY,
    next_run_time TIMESTAMP WITH TIME ZONE,
    job_state BYTEA NOT NULL
);

COMMENT ON TABLE apscheduler_jobs IS '定时任务调度器任务表';
COMMENT ON COLUMN apscheduler_jobs.id IS '任务标识ID';
COMMENT ON COLUMN apscheduler_jobs.next_run_time IS '下次执行时间';
COMMENT ON COLUMN apscheduler_jobs.job_state IS '任务状态数据';

-- ============================================
-- 外汇市场数据表（第一阶段实施）
-- ============================================

-- 外汇标的基础信息表
CREATE TABLE IF NOT EXISTS forex_symbols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    datasource_id UUID REFERENCES datasources(id),
    base_currency VARCHAR(10),
    quote_currency VARCHAR(10),
    is_active BOOLEAN DEFAULT true,
    first_trade_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE forex_symbols IS '外汇标的基础信息表';
COMMENT ON COLUMN forex_symbols.id IS '货币对唯一标识ID';
COMMENT ON COLUMN forex_symbols.code IS '货币对代码（英文）';
COMMENT ON COLUMN forex_symbols.name IS '货币对名称（中文）';
COMMENT ON COLUMN forex_symbols.description IS '货币对描述说明';
COMMENT ON COLUMN forex_symbols.datasource_id IS '默认数据来源ID';
COMMENT ON COLUMN forex_symbols.base_currency IS '基础货币';
COMMENT ON COLUMN forex_symbols.quote_currency IS '计价货币';
COMMENT ON COLUMN forex_symbols.is_active IS '是否启用';
COMMENT ON COLUMN forex_symbols.first_trade_date IS '首次交易日期';
COMMENT ON COLUMN forex_symbols.created_at IS '创建时间';
COMMENT ON COLUMN forex_symbols.updated_at IS '更新时间';

-- 外汇日线行情表（分区表）
CREATE TABLE IF NOT EXISTS forex_daily (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol_id UUID NOT NULL REFERENCES forex_symbols(id),
    datasource_id UUID REFERENCES datasources(id),
    date DATE NOT NULL,
    open NUMERIC(10, 4),
    high NUMERIC(10, 4),
    low NUMERIC(10, 4),
    close NUMERIC(10, 4),
    change_pct NUMERIC(10, 4),
    change_amount NUMERIC(10, 4),
    amplitude NUMERIC(10, 4),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol_id, date, datasource_id)
) PARTITION BY RANGE (date);

COMMENT ON TABLE forex_daily IS '外汇日线行情数据表（按年分区）';
COMMENT ON COLUMN forex_daily.id IS '数据唯一标识ID';
COMMENT ON COLUMN forex_daily.symbol_id IS '关联货币对ID';
COMMENT ON COLUMN forex_daily.datasource_id IS '数据来源ID';
COMMENT ON COLUMN forex_daily.date IS '交易日期';
COMMENT ON COLUMN forex_daily.open IS '开盘价';
COMMENT ON COLUMN forex_daily.high IS '最高价';
COMMENT ON COLUMN forex_daily.low IS '最低价';
COMMENT ON COLUMN forex_daily.close IS '收盘价';
COMMENT ON COLUMN forex_daily.change_pct IS '涨跌幅（百分比）';
COMMENT ON COLUMN forex_daily.change_amount IS '涨跌额';
COMMENT ON COLUMN forex_daily.amplitude IS '振幅（百分比）';
COMMENT ON COLUMN forex_daily.updated_at IS '数据更新时间';

-- 创建外汇日线分区表
CREATE TABLE IF NOT EXISTS forex_daily_2024 PARTITION OF forex_daily
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE IF NOT EXISTS forex_daily_2025 PARTITION OF forex_daily
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE IF NOT EXISTS forex_daily_2026 PARTITION OF forex_daily
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE TABLE IF NOT EXISTS forex_daily_default PARTITION OF forex_daily
    DEFAULT;

-- ============================================
-- 创建索引
-- ============================================

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Session表索引
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

-- 市场表索引
CREATE INDEX IF NOT EXISTS idx_markets_code ON markets(code);

-- 数据源表索引
CREATE INDEX IF NOT EXISTS idx_datasources_market ON datasources(market_id);

-- 采集任务表索引
CREATE INDEX IF NOT EXISTS idx_collection_tasks_datasource ON collection_tasks(datasource_id);
CREATE INDEX IF NOT EXISTS idx_collection_tasks_market ON collection_tasks(market_id);
CREATE INDEX IF NOT EXISTS idx_collection_tasks_enabled ON collection_tasks(is_enabled);
CREATE INDEX IF NOT EXISTS idx_collection_tasks_next_run ON collection_tasks(next_run_at);

-- 采集任务日志表索引
CREATE INDEX IF NOT EXISTS idx_task_logs_task ON collection_task_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_task_logs_run_at ON collection_task_logs(run_at);
CREATE INDEX IF NOT EXISTS idx_task_logs_status ON collection_task_logs(status);

-- 外汇标的表索引
CREATE INDEX IF NOT EXISTS idx_forex_symbols_code ON forex_symbols(code);
CREATE INDEX IF NOT EXISTS idx_forex_symbols_datasource ON forex_symbols(datasource_id);
CREATE INDEX IF NOT EXISTS idx_forex_symbols_active ON forex_symbols(is_active);

-- 外汇日线表索引（每个分区自动继承）
CREATE INDEX IF NOT EXISTS idx_forex_daily_symbol_date ON forex_daily(symbol_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_forex_daily_date ON forex_daily(date DESC);
CREATE INDEX IF NOT EXISTS idx_forex_daily_datasource ON forex_daily(datasource_id);

-- APScheduler任务表索引
CREATE INDEX IF NOT EXISTS idx_apscheduler_jobs_next_run_time ON apscheduler_jobs(next_run_time);

-- ============================================
-- 初始数据插入
-- ============================================

-- 插入默认admin用户
INSERT INTO users (username, password_hash, role)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0L5qN.$2b$12$LQv3c1yqBWVHxkd0L5qN.placeholder', 'admin')
ON CONFLICT (username) DO NOTHING;

-- 插入市场类型数据
INSERT INTO markets (code, name, description, timezone) VALUES
('forex', '外汇', '外汇货币对市场', 'UTC'),
('stock_cn', 'A股', '中国A股市场', 'Asia/Shanghai'),
('stock_us', '美股', '美国股票市场', 'America/New_York'),
('stock_hk', '港股', '香港股票市场', 'Asia/Hong_Kong'),
('futures_cn', '国内期货', '中国期货市场', 'Asia/Shanghai'),
('crypto', '数字货币', '数字货币市场', 'UTC')
ON CONFLICT (code) DO NOTHING;

-- 插入外汇数据源配置
INSERT INTO datasources (name, market_id, interface, description, config_schema, supported_symbols, min_date, type, is_active)
SELECT
    'AKShare外汇历史数据',
    m.id,
    'forex_hist',
    'AKShare外汇历史行情数据接口，提供各货币对的日线OHLC数据',
    '{
        "fields": [
            {"name": "symbol", "label": "货币对", "type": "select", "required": true, "options_source": "supported_symbols"},
            {"name": "start_date", "label": "开始日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"},
            {"name": "end_date", "label": "结束日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"}
        ]
    }',
    '["美元人民币", "欧元人民币", "日元人民币", "英镑人民币", "港币人民币", "澳元人民币", "加元人民币", "瑞郎人民币", "新西兰元人民币", "欧元美元", "英镑美元", "美元日元", "澳元美元", "美元加元", "美元瑞郎", "新西兰元美元", "欧元英镑", "欧元日元", "英镑日元", "澳元日元"]',
    '1994-01-01',
    'akshare',
    true
FROM markets m WHERE m.code = 'forex'
ON CONFLICT (name) DO NOTHING;

-- 插入外汇货币对标的基础数据
INSERT INTO forex_symbols (code, name, base_currency, quote_currency, is_active) VALUES
('USDCNY', '美元人民币', 'USD', 'CNY', true),
('EURCNY', '欧元人民币', 'EUR', 'CNY', true),
('JPYCNY', '日元人民币', 'JPY', 'CNY', true),
('GBPCNY', '英镑人民币', 'GBP', 'CNY', true),
('HKDCNY', '港币人民币', 'HKD', 'CNY', true),
('AUDCNY', '澳元人民币', 'AUD', 'CNY', true),
('CADCNY', '加元人民币', 'CAD', 'CNY', true),
('CHFCNY', '瑞郎人民币', 'CHF', 'CNY', true),
('NZDCNY', '新西兰元人民币', 'NZD', 'CNY', true),
('EURUSD', '欧元美元', 'EUR', 'USD', true),
('GBPUSD', '英镑美元', 'GBP', 'USD', true),
('USDJPY', '美元日元', 'USD', 'JPY', true),
('AUDUSD', '澳元美元', 'AUD', 'USD', true),
('USDCAD', '美元加元', 'USD', 'CAD', true),
('USDCHF', '美元瑞郎', 'USD', 'CHF', true),
('NZDUSD', '新西兰元美元', 'NZD', 'USD', true),
('EURGBP', '欧元英镑', 'EUR', 'GBP', true),
('EURJPY', '欧元日元', 'EUR', 'JPY', true),
('GBPJPY', '英镑日元', 'GBP', 'JPY', true),
('AUDJPY', '澳元日元', 'AUD', 'JPY', true)
ON CONFLICT (code) DO NOTHING;