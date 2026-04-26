-- 数据库迁移脚本 0424
-- 统一 user_id 类型为 INTEGER，清理旧测试数据

BEGIN TRANSACTION;

-- 清空旧测试订单和订阅，重建为 INTEGER 类型
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS subscriptions;

-- 重建 orders 表（user_id INTEGER）
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no VARCHAR NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    amount FLOAT NOT NULL,
    paid_amount FLOAT DEFAULT 0,
    status VARCHAR DEFAULT 'pending',
    product_name VARCHAR,
    description TEXT,
    transaction_id VARCHAR,
    fail_reason TEXT,
    paid_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 重建 subscriptions 表（user_id INTEGER）
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan_type VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'active',
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expire_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 清理 users 表残留 clerk_id（如果存在）
-- SQLite 不支持直接删除列，需要重建表
-- 但这里我们只删除数据，保留表结构

COMMIT;
