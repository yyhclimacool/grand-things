-- PostgreSQL 数据库初始化脚本
-- 为 Grand Things 应用添加必要的扩展和配置

-- 创建 UUID 扩展（用于生成唯一标识符）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建 pg_trgm 扩展（用于文本搜索和相似度匹配）
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 创建 unaccent 扩展（用于去除重音符号的文本搜索）
CREATE EXTENSION IF NOT EXISTS unaccent;

-- 设置时区为 UTC
SET timezone = 'UTC';

-- 创建数据库用户（如果需要）
-- 注意：在 Docker 环境中通常不需要这个，因为会使用 POSTGRES_USER
-- DO $$ 
-- BEGIN
--     IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'grand_things_user') THEN
--         CREATE ROLE grand_things_user WITH LOGIN PASSWORD 'your_secure_password';
--         GRANT CONNECT ON DATABASE grand_things TO grand_things_user;
--         GRANT USAGE ON SCHEMA public TO grand_things_user;
--         GRANT CREATE ON SCHEMA public TO grand_things_user;
--     END IF;
-- END $$;

-- 输出初始化完成信息
SELECT 'Grand Things PostgreSQL 数据库初始化完成！' as status; 