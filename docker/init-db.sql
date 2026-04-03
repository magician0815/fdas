-- FDAS 数据库初始化脚本
-- 金融数据抓取与分析系统

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Session表（服务端Session存储）
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- 数据源配置表
CREATE TABLE IF NOT EXISTS datasources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'akshare',
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 采集任务表
CREATE TABLE IF NOT EXISTS collection_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    datasource_id UUID NOT NULL REFERENCES datasources(id) ON DELETE CASCADE,
    target_data VARCHAR(100) NOT NULL,
    cron_expression VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 汇率数据表
CREATE TABLE IF NOT EXISTS fx_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10, 4),
    high DECIMAL(10, 4),
    low DECIMAL(10, 4),
    close DECIMAL(10, 4),
    volume BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);

-- APScheduler任务表
CREATE TABLE IF NOT EXISTS apscheduler_jobs (
    id VARCHAR(255) PRIMARY KEY,
    next_run_time TIMESTAMP WITH TIME ZONE,
    job_state BYTEA NOT NULL
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_fx_data_symbol ON fx_data(symbol);
CREATE INDEX IF NOT EXISTS idx_fx_data_date ON fx_data(date);
CREATE INDEX IF NOT EXISTS idx_fx_data_symbol_date ON fx_data(symbol, date);
CREATE INDEX IF NOT EXISTS idx_collection_tasks_datasource_id ON collection_tasks(datasource_id);
CREATE INDEX IF NOT EXISTS idx_apscheduler_jobs_next_run_time ON apscheduler_jobs(next_run_time);

-- 插入默认admin用户（密码需要在应用启动后修改）
-- 密码: admin123 (bcrypt hash示例，实际应在应用中生成)
INSERT INTO users (username, password_hash, role)
VALUES ('admin', 'placeholder_change_on_first_login', 'admin')
ON CONFLICT (username) DO NOTHING;

-- 插入默认数据源配置
INSERT INTO datasources (name, type, config, is_active)
VALUES ('AKShare外汇数据', 'akshare', '{"source": "fx_spot", "symbol_mapping": {"USDCNH": "美元/离岸人民币"}}', true)
ON CONFLICT DO NOTHING;