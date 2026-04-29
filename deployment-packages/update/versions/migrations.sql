-- FDAS数据库增量迁移模板
-- 版本: 2.1.0 (示例)
-- 日期: 2026-04-XX
-- 说明: 此模板用于版本升级时的数据库结构变更

-- ============================================
-- 迁移前检查
-- ============================================
-- 验证当前数据库版本
SELECT value FROM system_info WHERE key = 'db_version';

-- ============================================
-- 表结构变更
-- ============================================

-- 示例: 添加新字段（使用IF NOT EXISTS避免重复执行）
-- ALTER TABLE forex_symbols ADD COLUMN IF NOT EXISTS decimal_places INTEGER DEFAULT 4;
-- COMMENT ON COLUMN forex_symbols.decimal_places IS '价格小数位数';

-- 示例: 创建新表
-- CREATE TABLE IF NOT EXISTS forex_intraday (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     symbol_id UUID NOT NULL REFERENCES forex_symbols(id),
--     timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
--     open NUMERIC(10,4),
--     high NUMERIC(10,4),
--     low NUMERIC(10,4),
--     close NUMERIC(10,4),
--     volume BIGINT DEFAULT 0,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- ) PARTITION BY RANGE (timestamp);
--
-- COMMENT ON TABLE forex_intraday IS '外汇分钟线行情表';

-- 示例: 创建分区
-- CREATE TABLE IF NOT EXISTS forex_intraday_2026 PARTITION OF forex_intraday
--     FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- ============================================
-- 索引变更
-- ============================================

-- 示例: 创建新索引
-- CREATE INDEX IF NOT EXISTS idx_forex_intraday_symbol_ts
--     ON forex_intraday(symbol_id, timestamp DESC);

-- 示例: 删除旧索引（谨慎操作）
-- DROP INDEX IF EXISTS idx_old_index_name;

-- ============================================
-- 数据迁移
-- ============================================

-- 示例: 更新现有数据
-- UPDATE forex_symbols SET decimal_places = 4 WHERE decimal_places IS NULL;

-- 示例: 插入新数据
-- INSERT INTO markets (code, name, description) VALUES
-- ('new_market', '新市场', '新市场描述')
-- ON CONFLICT (code) DO NOTHING;

-- ============================================
-- 版本记录
-- ============================================

-- 创建版本记录表（如果不存在）
CREATE TABLE IF NOT EXISTS system_info (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE system_info IS '系统信息记录表';

-- 更新版本号
INSERT INTO system_info (key, value) VALUES ('db_version', '2.1.0')
ON CONFLICT (key) DO UPDATE SET value = '2.1.0', updated_at = CURRENT_TIMESTAMP;

-- ============================================
-- 迁移后验证
-- ============================================

-- 验证版本
SELECT * FROM system_info WHERE key = 'db_version';

-- 验证表结构变更
-- SELECT column_name, data_type FROM information_schema.columns
-- WHERE table_name = 'forex_symbols' AND column_name = 'decimal_places';

-- ============================================
-- 完成标记
-- ============================================
-- 迁移脚本执行完成后，请检查:
-- 1. 版本号是否正确更新
-- 2. 新表/字段是否正确创建
-- 3. 索引是否正确创建
-- 4. 数据是否正确迁移