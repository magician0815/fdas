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
    ip_address VARCHAR(45) NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

COMMENT ON TABLE sessions IS '用户登录会话信息表';
COMMENT ON COLUMN sessions.id IS '会话唯一标识ID';
COMMENT ON COLUMN sessions.user_id IS '关联用户ID';
COMMENT ON COLUMN sessions.session_data IS '会话数据';
COMMENT ON COLUMN sessions.ip_address IS '创建会话时的IP地址（IPv4/IPv6）';
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
    config_file TEXT,
    config_version VARCHAR(20),
    config_updated_at TIMESTAMP WITH TIME ZONE,
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
COMMENT ON COLUMN datasources.config_file IS '数据源配置文件(JSON格式)';
COMMENT ON COLUMN datasources.config_version IS '配置版本号';
COMMENT ON COLUMN datasources.config_updated_at IS '配置更新时间';
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
    id UUID DEFAULT uuid_generate_v4(),
    symbol_id UUID NOT NULL REFERENCES forex_symbols(id),
    datasource_id UUID REFERENCES datasources(id),
    date DATE NOT NULL,
    open NUMERIC(10, 4),
    high NUMERIC(10, 4),
    low NUMERIC(10, 4),
    close NUMERIC(10, 4),
    volume BIGINT DEFAULT 0,
    change_pct NUMERIC(10, 4),
    change_amount NUMERIC(10, 4),
    amplitude NUMERIC(10, 4),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, date),
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
COMMENT ON COLUMN forex_daily.volume IS '成交量（外汇数据通常为0）';
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

-- 用户图表配置表（存储画线工具设置、主题偏好等）
CREATE TABLE IF NOT EXISTS user_chart_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    setting_type VARCHAR(50) NOT NULL,
    setting_key VARCHAR(100) NOT NULL,
    setting_value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, setting_type, setting_key)
);

COMMENT ON TABLE user_chart_settings IS '用户图表个性化配置存储表';
COMMENT ON COLUMN user_chart_settings.id IS '配置记录唯一标识ID';
COMMENT ON COLUMN user_chart_settings.user_id IS '关联用户ID';
COMMENT ON COLUMN user_chart_settings.setting_type IS '配置类型（drawing_tools/theme/indicators/view）';
COMMENT ON COLUMN user_chart_settings.setting_key IS '配置键名';
COMMENT ON COLUMN user_chart_settings.setting_value IS '配置值（JSON格式）';
COMMENT ON COLUMN user_chart_settings.created_at IS '创建时间';
COMMENT ON COLUMN user_chart_settings.updated_at IS '更新时间';

-- 数据源配置向导会话表
CREATE TABLE IF NOT EXISTS datasource_wizard_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    current_step INTEGER NOT NULL DEFAULT 1,
    datasource_name VARCHAR(100),
    market_id UUID REFERENCES markets(id),
    api_base_url TEXT,
    api_method VARCHAR(10),
    api_timeout INTEGER,
    api_headers JSONB,
    selected_endpoint TEXT,
    available_endpoints JSONB,
    sample_data JSONB,
    field_mapping JSONB,
    test_result JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE datasource_wizard_sessions IS '数据源配置向导会话表';
COMMENT ON COLUMN datasource_wizard_sessions.id IS '会话唯一标识ID';
COMMENT ON COLUMN datasource_wizard_sessions.user_id IS '创建用户ID';
COMMENT ON COLUMN datasource_wizard_sessions.current_step IS '当前步骤(1-7)';
COMMENT ON COLUMN datasource_wizard_sessions.datasource_name IS '数据源名称';
COMMENT ON COLUMN datasource_wizard_sessions.market_id IS '市场ID';
COMMENT ON COLUMN datasource_wizard_sessions.api_base_url IS 'API基础URL';
COMMENT ON COLUMN datasource_wizard_sessions.api_method IS '请求方法(GET/POST)';
COMMENT ON COLUMN datasource_wizard_sessions.api_timeout IS '超时时间(秒)';
COMMENT ON COLUMN datasource_wizard_sessions.api_headers IS '请求头JSON';
COMMENT ON COLUMN datasource_wizard_sessions.selected_endpoint IS '选中的数据端点路径';
COMMENT ON COLUMN datasource_wizard_sessions.available_endpoints IS '发现的可用端点列表';
COMMENT ON COLUMN datasource_wizard_sessions.sample_data IS '样本数据预览';
COMMENT ON COLUMN datasource_wizard_sessions.field_mapping IS '字段映射配置';
COMMENT ON COLUMN datasource_wizard_sessions.test_result IS '测试采集结果';
COMMENT ON COLUMN datasource_wizard_sessions.status IS '会话状态(in_progress/completed/failed)';
COMMENT ON COLUMN datasource_wizard_sessions.error_message IS '错误信息';
COMMENT ON COLUMN datasource_wizard_sessions.created_at IS '创建时间';
COMMENT ON COLUMN datasource_wizard_sessions.updated_at IS '更新时间';

-- 创建向导会话表索引
CREATE INDEX IF NOT EXISTS idx_wizard_user ON datasource_wizard_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_wizard_status ON datasource_wizard_sessions(status);

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

-- 用户图表配置表索引
CREATE INDEX IF NOT EXISTS idx_user_chart_settings_user ON user_chart_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_user_chart_settings_type ON user_chart_settings(setting_type);

-- APScheduler任务表索引
CREATE INDEX IF NOT EXISTS idx_apscheduler_jobs_next_run_time ON apscheduler_jobs(next_run_time);

-- ============================================
-- 初始数据插入
-- ============================================

-- 插入默认admin用户
-- ⚠️ 安全警告: 默认密码为 'admin123'，生产环境部署后必须立即修改！
-- 密码哈希使用bcrypt算法(rounds=12)，对应明文密码 'admin123'
-- 首次登录后请通过用户管理界面修改密码
INSERT INTO users (username, password_hash, role)
VALUES ('admin', '$2b$12$fhlKutShR.oSCYLHLIZvI.iMwPv.LuGEsVar3bj7.GHmRe.KL2eAq', 'admin')
ON CONFLICT (username) DO NOTHING;

-- 插入市场类型数据
INSERT INTO markets (code, name, description, timezone) VALUES
('forex', '外汇', '外汇货币对市场', 'UTC'),
('stock_cn', 'A股', '中国A股市场', 'Asia/Shanghai'),
('stock_us', '美股', '美国股票市场', 'America/New_York'),
('stock_hk', '港股', '香港股票市场', 'Asia/Hong_Kong'),
('futures_cn', '国内期货', '中国期货市场', 'Asia/Shanghai'),
('bond_cn', '国内债券', '中国债券市场', 'Asia/Shanghai'),
('bond_us', '美国债券', '美国债券市场', 'America/New_York'),
('crypto', '数字货币', '数字货币市场', 'UTC')
ON CONFLICT (code) DO NOTHING;

-- 插入外汇数据源配置（包含默认配置文件）
INSERT INTO datasources (name, market_id, interface, description, config_schema, supported_symbols, min_date, type, is_active, config_file, config_version, config_updated_at)
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
    true,
    '{
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
}',
    '1.0',
    CURRENT_TIMESTAMP
FROM markets m WHERE m.code = 'forex'
ON CONFLICT (name) DO NOTHING;

-- 插入外汇货币对标的基础数据（使用AKShare标准代码）
-- AKShare代码说明：CNH=离岸人民币，CNYC=人民币中间价
INSERT INTO forex_symbols (code, name, base_currency, quote_currency, is_active) VALUES
('USDCNH', '美元离岸人民币', 'USD', 'CNH', true),
('EURCNH', '欧元离岸人民币', 'EUR', 'CNH', true),
('CNHJPY', '离岸人民币日元', 'CNH', 'JPY', true),
('GBPCNH', '英镑离岸人民币', 'GBP', 'CNH', true),
('CNHHKD', '离岸人民币港币', 'CNH', 'HKD', true),
('AUDCNH', '澳元离岸人民币', 'AUD', 'CNH', true),
('CADCNH', '加元离岸人民币', 'CAD', 'CNH', true),
('CHFCNH', '瑞郎离岸人民币', 'CHF', 'CNH', true),
('NZDCNH', '新西兰元离岸人民币', 'NZD', 'CNH', true),
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

-- ============================================
-- 期货市场数据表（P6阶段实施）
-- ============================================

-- 期货品种基础信息表
CREATE TABLE IF NOT EXISTS futures_varieties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    market_id UUID REFERENCES markets(id),
    contract_unit NUMERIC(10, 2),
    min_price_tick NUMERIC(10, 4),
    trading_months VARCHAR(50),
    delivery_months VARCHAR(50),
    delivery_method VARCHAR(20),
    last_trade_day_rule TEXT,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE futures_varieties IS '期货品种基础信息表';
COMMENT ON COLUMN futures_varieties.id IS '品种唯一标识ID';
COMMENT ON COLUMN futures_varieties.code IS '品种代码（如IF、IC、AU）';
COMMENT ON COLUMN futures_varieties.name IS '品种名称（如沪深300股指期货）';
COMMENT ON COLUMN futures_varieties.exchange IS '交易所代码（CFFEX/SHFE/DCE/CZCE）';
COMMENT ON COLUMN futures_varieties.market_id IS '所属市场ID';
COMMENT ON COLUMN futures_varieties.contract_unit IS '合约单位（元/点或吨/手）';
COMMENT ON COLUMN futures_varieties.min_price_tick IS '最小变动价位';
COMMENT ON COLUMN futures_varieties.trading_months IS '交易月份规则';
COMMENT ON COLUMN futures_varieties.delivery_months IS '交割月份规则';
COMMENT ON COLUMN futures_varieties.delivery_method IS '交割方式';
COMMENT ON COLUMN futures_varieties.last_trade_day_rule IS '最后交易日规则描述';
COMMENT ON COLUMN futures_varieties.description IS '品种描述说明';
COMMENT ON COLUMN futures_varieties.is_active IS '是否启用';
COMMENT ON COLUMN futures_varieties.created_at IS '创建时间';
COMMENT ON COLUMN futures_varieties.updated_at IS '更新时间';

-- 期货合约信息表
CREATE TABLE IF NOT EXISTS futures_contracts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    variety_id UUID NOT NULL REFERENCES futures_varieties(id),
    contract_code VARCHAR(20) UNIQUE NOT NULL,
    contract_name VARCHAR(100) NOT NULL,
    contract_month VARCHAR(10) NOT NULL,
    year VARCHAR(4) NOT NULL,
    month VARCHAR(2) NOT NULL,
    listing_date DATE,
    last_trade_date DATE NOT NULL,
    delivery_date DATE,
    is_main_contract BOOLEAN DEFAULT false,
    main_start_date DATE,
    main_end_date DATE,
    open_interest NUMERIC(20, 0) DEFAULT 0,
    datasource_id UUID REFERENCES datasources(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE futures_contracts IS '期货合约信息表';
COMMENT ON COLUMN futures_contracts.id IS '合约唯一标识ID';
COMMENT ON COLUMN futures_contracts.variety_id IS '关联品种ID';
COMMENT ON COLUMN futures_contracts.contract_code IS '合约代码（如IF2401）';
COMMENT ON COLUMN futures_contracts.contract_name IS '合约名称';
COMMENT ON COLUMN futures_contracts.contract_month IS '合约月份标识';
COMMENT ON COLUMN futures_contracts.year IS '合约年份';
COMMENT ON COLUMN futures_contracts.month IS '合约月份（01-12）';
COMMENT ON COLUMN futures_contracts.listing_date IS '上市日期';
COMMENT ON COLUMN futures_contracts.last_trade_date IS '最后交易日/到期日';
COMMENT ON COLUMN futures_contracts.delivery_date IS '交割日';
COMMENT ON COLUMN futures_contracts.is_main_contract IS '是否为当前主力合约';
COMMENT ON COLUMN futures_contracts.main_start_date IS '成为主力合约的开始日期';
COMMENT ON COLUMN futures_contracts.main_end_date IS '作为主力合约的结束日期';
COMMENT ON COLUMN futures_contracts.open_interest IS '当前持仓量';
COMMENT ON COLUMN futures_contracts.datasource_id IS '数据来源ID';
COMMENT ON COLUMN futures_contracts.is_active IS '是否启用（已到期设为False）';
COMMENT ON COLUMN futures_contracts.created_at IS '创建时间';
COMMENT ON COLUMN futures_contracts.updated_at IS '更新时间';

-- 期货日线行情表（分区表）
CREATE TABLE IF NOT EXISTS futures_daily (
    id UUID DEFAULT uuid_generate_v4(),
    contract_id UUID NOT NULL REFERENCES futures_contracts(id),
    variety_id UUID NOT NULL REFERENCES futures_varieties(id),
    datasource_id UUID REFERENCES datasources(id),
    date DATE NOT NULL,
    open NUMERIC(10, 4),
    high NUMERIC(10, 4),
    low NUMERIC(10, 4),
    close NUMERIC(10, 4),
    settle_price NUMERIC(10, 4),
    volume BIGINT DEFAULT 0,
    open_interest BIGINT DEFAULT 0,
    turnover NUMERIC(20, 2) DEFAULT 0,
    change_pct NUMERIC(10, 4),
    change_amount NUMERIC(10, 4),
    amplitude NUMERIC(10, 4),
    oi_change BIGINT DEFAULT 0,
    is_main_data BOOLEAN DEFAULT false,
    adjusted_price NUMERIC(10, 4),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, date),
    UNIQUE(contract_id, date, datasource_id)
) PARTITION BY RANGE (date);

COMMENT ON TABLE futures_daily IS '期货日线行情数据表（按年分区）';
COMMENT ON COLUMN futures_daily.id IS '数据唯一标识ID';
COMMENT ON COLUMN futures_daily.contract_id IS '关联合约ID';
COMMENT ON COLUMN futures_daily.variety_id IS '关联品种ID';
COMMENT ON COLUMN futures_daily.datasource_id IS '数据来源ID';
COMMENT ON COLUMN futures_daily.date IS '交易日期';
COMMENT ON COLUMN futures_daily.open IS '开盘价';
COMMENT ON COLUMN futures_daily.high IS '最高价';
COMMENT ON COLUMN futures_daily.low IS '最低价';
COMMENT ON COLUMN futures_daily.close IS '收盘价';
COMMENT ON COLUMN futures_daily.settle_price IS '结算价';
COMMENT ON COLUMN futures_daily.volume IS '成交量';
COMMENT ON COLUMN futures_daily.open_interest IS '持仓量（OI）';
COMMENT ON COLUMN futures_daily.turnover IS '成交金额';
COMMENT ON COLUMN futures_daily.change_pct IS '涨跌幅（百分比）';
COMMENT ON COLUMN futures_daily.change_amount IS '涨跌额';
COMMENT ON COLUMN futures_daily.amplitude IS '振幅（百分比）';
COMMENT ON COLUMN futures_daily.oi_change IS '持仓量变化';
COMMENT ON COLUMN futures_daily.is_main_data IS '是否为主力合约数据';
COMMENT ON COLUMN futures_daily.adjusted_price IS '挢月调整后价格';
COMMENT ON COLUMN futures_daily.updated_at IS '数据更新时间';

-- 创建期货日线分区表
CREATE TABLE IF NOT EXISTS futures_daily_2024 PARTITION OF futures_daily
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE IF NOT EXISTS futures_daily_2025 PARTITION OF futures_daily
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE IF NOT EXISTS futures_daily_2026 PARTITION OF futures_daily
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE TABLE IF NOT EXISTS futures_daily_default PARTITION OF futures_daily
    DEFAULT;

-- ============================================
-- 期货市场索引
-- ============================================

-- 期货品种表索引
CREATE INDEX IF NOT EXISTS idx_futures_varieties_code ON futures_varieties(code);
CREATE INDEX IF NOT EXISTS idx_futures_varieties_exchange ON futures_varieties(exchange);
CREATE INDEX IF NOT EXISTS idx_futures_varieties_market ON futures_varieties(market_id);
CREATE INDEX IF NOT EXISTS idx_futures_varieties_active ON futures_varieties(is_active);

-- 期货合约表索引
CREATE INDEX IF NOT EXISTS idx_futures_contracts_code ON futures_contracts(contract_code);
CREATE INDEX IF NOT EXISTS idx_futures_contracts_variety ON futures_contracts(variety_id);
CREATE INDEX IF NOT EXISTS idx_futures_contracts_main ON futures_contracts(is_main_contract);
CREATE INDEX IF NOT EXISTS idx_futures_contracts_active ON futures_contracts(is_active);
CREATE INDEX IF NOT EXISTS idx_futures_contracts_last_trade ON futures_contracts(last_trade_date);

-- 期货日线表索引
CREATE INDEX IF NOT EXISTS idx_futures_daily_contract_date ON futures_daily(contract_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_futures_daily_variety_date ON futures_daily(variety_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_futures_daily_date ON futures_daily(date DESC);
CREATE INDEX IF NOT EXISTS idx_futures_daily_main ON futures_daily(is_main_data);
CREATE INDEX IF NOT EXISTS idx_futures_daily_datasource ON futures_daily(datasource_id);

-- ============================================
-- 期货品种初始数据
-- ============================================

-- 插入主要期货品种数据
INSERT INTO futures_varieties (code, name, exchange, market_id, contract_unit, min_price_tick, trading_months, delivery_method, last_trade_day_rule, description, is_active)
SELECT
    'IF', '沪深300股指期货', 'CFFEX', m.id, 300.00, 0.2, '当月、下月及随后两个季月', 'cash_delivery', '合约到期月份的第三个周五', '沪深300指数期货，现金交割', true
FROM markets m WHERE m.code = 'futures_cn'
ON CONFLICT (code) DO NOTHING;

INSERT INTO futures_varieties (code, name, exchange, market_id, contract_unit, min_price_tick, trading_months, delivery_method, last_trade_day_rule, description, is_active)
SELECT
    'IC', '中证500股指期货', 'CFFEX', m.id, 200.00, 0.2, '当月、下月及随后两个季月', 'cash_delivery', '合约到期月份的第三个周五', '中证500指数期货，现金交割', true
FROM markets m WHERE m.code = 'futures_cn'
ON CONFLICT (code) DO NOTHING;

INSERT INTO futures_varieties (code, name, exchange, market_id, contract_unit, min_price_tick, trading_months, delivery_method, last_trade_day_rule, description, is_active)
SELECT
    'IH', '上证50股指期货', 'CFFEX', m.id, 300.00, 0.2, '当月、下月及随后两个季月', 'cash_delivery', '合约到期月份的第三个周五', '上证50指数期货，现金交割', true
FROM markets m WHERE m.code = 'futures_cn'
ON CONFLICT (code) DO NOTHING;

INSERT INTO futures_varieties (code, name, exchange, market_id, contract_unit, min_price_tick, trading_months, delivery_method, last_trade_day_rule, description, is_active)
SELECT
    'AU', '黄金期货', 'SHFE', m.id, 1000.00, 0.01, '1-12月', 'physical_delivery', '合约月份的15日', '上海期货交易所黄金期货，实物交割', true
FROM markets m WHERE m.code = 'futures_cn'
ON CONFLICT (code) DO NOTHING;

INSERT INTO futures_varieties (code, name, exchange, market_id, contract_unit, min_price_tick, trading_months, delivery_method, last_trade_day_rule, description, is_active)
SELECT
    'CU', '铜期货', 'SHFE', m.id, 5.00, 10.00, '1-12月', 'physical_delivery', '合约月份的15日', '上海期货交易所铜期货，实物交割', true
FROM markets m WHERE m.code = 'futures_cn'
ON CONFLICT (code) DO NOTHING;

-- ============================================
-- 股票市场数据表（Phase 2实施）
-- ============================================

-- 股票标的基础信息表（支持A股/美股/港股共享）
CREATE TABLE IF NOT EXISTS stock_symbols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    market_id UUID REFERENCES markets(id),
    exchange VARCHAR(20),
    industry VARCHAR(50),
    listing_date DATE,
    datasource_id UUID REFERENCES datasources(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE stock_symbols IS '股票标的基础信息表（支持A股/美股/港股）';
COMMENT ON COLUMN stock_symbols.id IS '股票唯一标识ID';
COMMENT ON COLUMN stock_symbols.code IS '股票代码';
COMMENT ON COLUMN stock_symbols.name IS '股票名称';
COMMENT ON COLUMN stock_symbols.market_id IS '所属市场ID（A股/美股/港股）';
COMMENT ON COLUMN stock_symbols.exchange IS '交易所代码';
COMMENT ON COLUMN stock_symbols.industry IS '所属行业';
COMMENT ON COLUMN stock_symbols.listing_date IS '上市日期';
COMMENT ON COLUMN stock_symbols.datasource_id IS '数据来源ID';
COMMENT ON COLUMN stock_symbols.is_active IS '是否启用';
COMMENT ON COLUMN stock_symbols.created_at IS '创建时间';
COMMENT ON COLUMN stock_symbols.updated_at IS '更新时间';

-- 股票日线行情表（分区表）
CREATE TABLE IF NOT EXISTS stock_daily (
    id UUID DEFAULT uuid_generate_v4(),
    symbol_id UUID NOT NULL REFERENCES stock_symbols(id),
    market_id UUID NOT NULL REFERENCES markets(id),
    datasource_id UUID REFERENCES datasources(id),
    date DATE NOT NULL,
    open NUMERIC(10, 4),
    high NUMERIC(10, 4),
    low NUMERIC(10, 4),
    close NUMERIC(10, 4),
    volume BIGINT DEFAULT 0,
    amount NUMERIC(20, 2) DEFAULT 0,
    turnover NUMERIC(10, 4),
    change_pct NUMERIC(10, 4),
    change_amount NUMERIC(10, 4),
    amplitude NUMERIC(10, 4),
    is_suspended BOOLEAN DEFAULT false,
    is_st BOOLEAN DEFAULT false,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, date),
    UNIQUE(symbol_id, market_id, date, datasource_id)
) PARTITION BY RANGE (date);

COMMENT ON TABLE stock_daily IS '股票日线行情数据表（按年分区，支持A股/美股/港股）';
COMMENT ON COLUMN stock_daily.id IS '数据唯一标识ID';
COMMENT ON COLUMN stock_daily.symbol_id IS '关联股票ID';
COMMENT ON COLUMN stock_daily.market_id IS '所属市场ID';
COMMENT ON COLUMN stock_daily.datasource_id IS '数据来源ID';
COMMENT ON COLUMN stock_daily.date IS '交易日期';
COMMENT ON COLUMN stock_daily.open IS '开盘价';
COMMENT ON COLUMN stock_daily.high IS '最高价';
COMMENT ON COLUMN stock_daily.low IS '最低价';
COMMENT ON COLUMN stock_daily.close IS '收盘价';
COMMENT ON COLUMN stock_daily.volume IS '成交量';
COMMENT ON COLUMN stock_daily.amount IS '成交额';
COMMENT ON COLUMN stock_daily.turnover IS '换手率（百分比）';
COMMENT ON COLUMN stock_daily.change_pct IS '涨跌幅（百分比）';
COMMENT ON COLUMN stock_daily.change_amount IS '涨跌额';
COMMENT ON COLUMN stock_daily.amplitude IS '振幅（百分比）';
COMMENT ON COLUMN stock_daily.is_suspended IS '是否停牌';
COMMENT ON COLUMN stock_daily.is_st IS '是否ST股票';
COMMENT ON COLUMN stock_daily.updated_at IS '数据更新时间';

-- 创建股票日线分区表
CREATE TABLE IF NOT EXISTS stock_daily_2024 PARTITION OF stock_daily
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE IF NOT EXISTS stock_daily_2025 PARTITION OF stock_daily
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE IF NOT EXISTS stock_daily_2026 PARTITION OF stock_daily
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE TABLE IF NOT EXISTS stock_daily_default PARTITION OF stock_daily
    DEFAULT;

-- ============================================
-- 债券市场数据表（Phase 2实施）
-- ============================================

-- 债券标的基础信息表（支持国内/国际债券共享）
CREATE TABLE IF NOT EXISTS bond_symbols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    market_id UUID REFERENCES markets(id),
    bond_type VARCHAR(20) NOT NULL,
    issuer VARCHAR(100),
    coupon_rate NUMERIC(10, 4),
    maturity_date DATE,
    face_value NUMERIC(12, 2),
    currency VARCHAR(10) DEFAULT 'CNY',
    rating VARCHAR(10),
    datasource_id UUID REFERENCES datasources(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE bond_symbols IS '债券标的基础信息表（支持国内/国际债券）';
COMMENT ON COLUMN bond_symbols.id IS '债券唯一标识ID';
COMMENT ON COLUMN bond_symbols.code IS '债券代码';
COMMENT ON COLUMN bond_symbols.name IS '债券名称';
COMMENT ON COLUMN bond_symbols.market_id IS '所属市场ID（国内债券/美国债券）';
COMMENT ON COLUMN bond_symbols.bond_type IS '债券类型（国债/企业债/可转债/金融债）';
COMMENT ON COLUMN bond_symbols.issuer IS '发行人';
COMMENT ON COLUMN bond_symbols.coupon_rate IS '票面利率（百分比）';
COMMENT ON COLUMN bond_symbols.maturity_date IS '到期日期';
COMMENT ON COLUMN bond_symbols.face_value IS '面值';
COMMENT ON COLUMN bond_symbols.currency IS '币种';
COMMENT ON COLUMN bond_symbols.rating IS '信用评级';
COMMENT ON COLUMN bond_symbols.datasource_id IS '数据来源ID';
COMMENT ON COLUMN bond_symbols.is_active IS '是否启用';
COMMENT ON COLUMN bond_symbols.created_at IS '创建时间';
COMMENT ON COLUMN bond_symbols.updated_at IS '更新时间';

-- 债券日线行情表（分区表）
-- 注意：分区表主键必须包含分区键(date)
CREATE TABLE IF NOT EXISTS bond_daily (
    id UUID DEFAULT uuid_generate_v4(),
    symbol_id UUID NOT NULL REFERENCES bond_symbols(id),
    market_id UUID NOT NULL REFERENCES markets(id),
    datasource_id UUID REFERENCES datasources(id),
    date DATE NOT NULL,
    open NUMERIC(18, 4),
    high NUMERIC(18, 4),
    low NUMERIC(18, 4),
    close NUMERIC(18, 4),
    yield_rate NUMERIC(12, 6),
    volume BIGINT DEFAULT 0,
    amount NUMERIC(24, 2) DEFAULT 0,
    change_pct NUMERIC(12, 4),
    change_amount NUMERIC(18, 4),
    amplitude NUMERIC(12, 4),
    duration NUMERIC(10, 4),
    convexity NUMERIC(10, 4),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol_id, date, id)
) PARTITION BY RANGE (date);

COMMENT ON TABLE bond_daily IS '债券日线行情数据表（按年分区，含收益率）';
COMMENT ON COLUMN bond_daily.id IS '数据唯一标识ID';
COMMENT ON COLUMN bond_daily.symbol_id IS '关联债券ID';
COMMENT ON COLUMN bond_daily.market_id IS '所属市场ID';
COMMENT ON COLUMN bond_daily.datasource_id IS '数据来源ID';
COMMENT ON COLUMN bond_daily.date IS '交易日期';
COMMENT ON COLUMN bond_daily.open IS '开盘价';
COMMENT ON COLUMN bond_daily.high IS '最高价';
COMMENT ON COLUMN bond_daily.low IS '最低价';
COMMENT ON COLUMN bond_daily.close IS '收盘价';
COMMENT ON COLUMN bond_daily.yield_rate IS '收益率（百分比）';
COMMENT ON COLUMN bond_daily.volume IS '成交量';
COMMENT ON COLUMN bond_daily.amount IS '成交额';
COMMENT ON COLUMN bond_daily.change_pct IS '涨跌幅（百分比）';
COMMENT ON COLUMN bond_daily.change_amount IS '涨跌额';
COMMENT ON COLUMN bond_daily.amplitude IS '振幅（百分比）';
COMMENT ON COLUMN bond_daily.updated_at IS '数据更新时间';

-- 创建债券日线分区表
CREATE TABLE IF NOT EXISTS bond_daily_2024 PARTITION OF bond_daily
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE IF NOT EXISTS bond_daily_2025 PARTITION OF bond_daily
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE IF NOT EXISTS bond_daily_2026 PARTITION OF bond_daily
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE TABLE IF NOT EXISTS bond_daily_default PARTITION OF bond_daily
    DEFAULT;

-- ============================================
-- 股票市场索引
-- ============================================

-- 股票标 的表索引
CREATE INDEX IF NOT EXISTS idx_stock_symbols_code ON stock_symbols(code);
CREATE INDEX IF NOT EXISTS idx_stock_symbols_market ON stock_symbols(market_id);
CREATE INDEX IF NOT EXISTS idx_stock_symbols_exchange ON stock_symbols(exchange);
CREATE INDEX IF NOT EXISTS idx_stock_symbols_active ON stock_symbols(is_active);

-- 股票日线表索引
CREATE INDEX IF NOT EXISTS idx_stock_daily_symbol_date ON stock_daily(symbol_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_stock_daily_market_date ON stock_daily(market_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_stock_daily_date ON stock_daily(date DESC);
CREATE INDEX IF NOT EXISTS idx_stock_daily_datasource ON stock_daily(datasource_id);

-- ============================================
-- 债券市场索引
-- ============================================

-- 债券标 的表索引
CREATE INDEX IF NOT EXISTS idx_bond_symbols_code ON bond_symbols(code);
CREATE INDEX IF NOT EXISTS idx_bond_symbols_market ON bond_symbols(market_id);
CREATE INDEX IF NOT EXISTS idx_bond_symbols_type ON bond_symbols(bond_type);
CREATE INDEX IF NOT EXISTS idx_bond_symbols_active ON bond_symbols(is_active);

-- 债券日线表索引
CREATE INDEX IF NOT EXISTS idx_bond_daily_symbol_date ON bond_daily(symbol_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_bond_daily_market_date ON bond_daily(market_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_bond_daily_date ON bond_daily(date DESC);
CREATE INDEX IF NOT EXISTS idx_bond_daily_datasource ON bond_daily(datasource_id);

-- ============================================
-- 股票默认数据源配置（Phase 2实施）
-- ============================================

-- 插入A股数据源配置
INSERT INTO datasources (name, market_id, interface, description, config_schema, supported_symbols, min_date, type, is_active, config_file, config_version, config_updated_at)
SELECT
    'AKShare A股历史数据',
    m.id,
    'stock_zh_a_hist',
    'AKShare A股历史行情数据接口，提供各股票的日线OHLC数据',
    '{
        "fields": [
            {"name": "symbol", "label": "股票代码", "type": "select", "required": true, "options_source": "supported_symbols"},
            {"name": "start_date", "label": "开始日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"},
            {"name": "end_date", "label": "结束日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"}
        ]
    }',
    NULL,
    '1990-01-01',
    'akshare',
    true,
    '{
  "version": "1.0",
  "name": "AKShare A股数据源",
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
}',
    '1.0',
    CURRENT_TIMESTAMP
FROM markets m WHERE m.code = 'stock_cn'
ON CONFLICT (name) DO NOTHING;

-- 插入美股数据源配置
INSERT INTO datasources (name, market_id, interface, description, config_schema, supported_symbols, min_date, type, is_active, config_file, config_version, config_updated_at)
SELECT
    'AKShare 美股历史数据',
    m.id,
    'stock_us_daily',
    'AKShare 美股历史行情数据接口',
    '{
        "fields": [
            {"name": "symbol", "label": "股票代码", "type": "select", "required": true, "options_source": "supported_symbols"},
            {"name": "start_date", "label": "开始日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"},
            {"name": "end_date", "label": "结束日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"}
        ]
    }',
    NULL,
    '1990-01-01',
    'akshare',
    true,
    '{
  "version": "1.0",
  "name": "AKShare 美股数据源",
  "type": "akshare",
  "market": "stock_us",
  "collector_type": "akshare_native",
  "akshare_interface": "stock_us_daily",
  "akshare_params": {
    "symbol": "AAPL",
    "period": "daily"
  }
}',
    '1.0',
    CURRENT_TIMESTAMP
FROM markets m WHERE m.code = 'stock_us'
ON CONFLICT (name) DO NOTHING;

-- 插入港股数据源配置
INSERT INTO datasources (name, market_id, interface, description, config_schema, supported_symbols, min_date, type, is_active, config_file, config_version, config_updated_at)
SELECT
    'AKShare 港股历史数据',
    m.id,
    'stock_hk_daily',
    'AKShare 港股历史行情数据接口',
    '{
        "fields": [
            {"name": "symbol", "label": "股票代码", "type": "select", "required": true, "options_source": "supported_symbols"},
            {"name": "start_date", "label": "开始日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"},
            {"name": "end_date", "label": "结束日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"}
        ]
    }',
    NULL,
    '1990-01-01',
    'akshare',
    true,
    '{
  "version": "1.0",
  "name": "AKShare 港股数据源",
  "type": "akshare",
  "market": "stock_hk",
  "collector_type": "akshare_native",
  "akshare_interface": "stock_hk_daily",
  "akshare_params": {
    "symbol": "00700"
  }
}',
    '1.0',
    CURRENT_TIMESTAMP
FROM markets m WHERE m.code = 'stock_hk'
ON CONFLICT (name) DO NOTHING;

-- 插入期货数据源配置
INSERT INTO datasources (name, market_id, interface, description, config_schema, supported_symbols, min_date, type, is_active, config_file, config_version, config_updated_at)
SELECT
    'AKShare 国内期货历史数据',
    m.id,
    'futures_zh_daily_sina',
    'AKShare 国内期货历史行情数据接口',
    '{
        "fields": [
            {"name": "symbol", "label": "期货代码", "type": "select", "required": true, "options_source": "supported_symbols"},
            {"name": "start_date", "label": "开始日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"},
            {"name": "end_date", "label": "结束日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"}
        ]
    }',
    NULL,
    '1990-01-01',
    'akshare',
    true,
    '{
  "version": "1.0",
  "name": "AKShare 期货数据源",
  "type": "akshare",
  "market": "futures_cn",
  "collector_type": "akshare_native",
  "akshare_interface": "futures_zh_daily_sina",
  "akshare_params": {
    "symbol": "IF9999"
  }
}',
    '1.0',
    CURRENT_TIMESTAMP
FROM markets m WHERE m.code = 'futures_cn'
ON CONFLICT (name) DO NOTHING;

-- 插入国内债券数据源配置
INSERT INTO datasources (name, market_id, interface, description, config_schema, supported_symbols, min_date, type, is_active, config_file, config_version, config_updated_at)
SELECT
    'AKShare 国内债券历史数据',
    m.id,
    'bond_cn_daily',
    'AKShare 国内债券历史行情数据接口',
    '{
        "fields": [
            {"name": "symbol", "label": "债券代码", "type": "select", "required": true, "options_source": "supported_symbols"},
            {"name": "start_date", "label": "开始日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"},
            {"name": "end_date", "label": "结束日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"}
        ]
    }',
    NULL,
    '1990-01-01',
    'akshare',
    true,
    '{
  "version": "1.0",
  "name": "AKShare 国内债券数据源",
  "type": "akshare",
  "market": "bond_cn",
  "collector_type": "akshare_native",
  "akshare_interface": "bond_cn_daily",
  "akshare_params": {
    "symbol": "113052"
  }
}',
    '1.0',
    CURRENT_TIMESTAMP
FROM markets m WHERE m.code = 'bond_cn'
ON CONFLICT (name) DO NOTHING;

-- 插入美国债券数据源配置
INSERT INTO datasources (name, market_id, interface, description, config_schema, supported_symbols, min_date, type, is_active, config_file, config_version, config_updated_at)
SELECT
    'AKShare 美国债券历史数据',
    m.id,
    'bond_us_daily',
    'AKShare 美国债券历史行情数据接口',
    '{
        "fields": [
            {"name": "symbol", "label": "债券代码", "type": "select", "required": true, "options_source": "supported_symbols"},
            {"name": "start_date", "label": "开始日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"},
            {"name": "end_date", "label": "结束日期", "type": "date", "required": true, "min_value_source": "min_date", "max_value": "today"}
        ]
    }',
    NULL,
    '1990-01-01',
    'akshare',
    true,
    '{
  "version": "1.0",
  "name": "AKShare 美国债���数据源",
  "type": "akshare",
  "market": "bond_us",
  "collector_type": "akshare_native",
  "akshare_interface": "bond_us_daily",
  "akshare_params": {
    "symbol": "US10Y"
  }
}',
    '1.0',
    CURRENT_TIMESTAMP
FROM markets m WHERE m.code = 'bond_us'
ON CONFLICT (name) DO NOTHING;