---
created: 2026-07-02
tags:
  - SQL
  - 基础
  - 数据库设计
---

# PK 与 FK 详解

> 数据库表设计的两个核心概念

---

## PK（Primary Key，主键）

**主键** 是表中用于 **唯一标识** 每一行记录的字段。

### 特点
| 特性 | 说明 |
|------|------|
| 唯一性 | 每一行的主键值都不同 |
| 非空 | 主键不能为 NULL |
| 唯一索引 | 数据库会自动为主键创建索引，加快查询速度 |
| 每表一个 | 每个表只能有一个主键（可以是多个字段组合） |

### 示例
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,      -- id 是主键
    name VARCHAR(50),
    email VARCHAR(100)
);

INSERT INTO users VALUES (1, '张三', 'zhangsan@.com');
INSERT INTO users VALUES (2, '李四', 'lisi@com');
-- INSERT INTO users VALUES (1, '王五', 'wangwu@com');  -- 报错！id=1 已存在
```

### 主键的命名习惯
- 通常叫 `id` 或 `表名_id`
- 如：`users` 表的主键叫 `id`，`orders` 表的主键叫 `id`

---

## FK（Foreign Key，外键）

**外键** 是一个表中的字段，它指向 **另一个表的主键**，用于建立表之间的关联关系。

### 特点
| 特性 | 说明 |
|------|------|
| 引用 | 外键的值必须在被引用表的主键中存在 |
| 可重复 | 外键值可以重复 |
| 可为空 | 外键可以为 NULL |
| 建立关系 | 用来实现表之间的 1:1、1:N、N:M 关系 |

### 示例
```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,                      -- user_id 是外键
    order_date DATE,
    amount DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(id)  -- 指向 users 表的 id
);

-- 正常插入
INSERT INTO users (id, name) VALUES (1, '张三');
INSERT INTO orders (id, user_id, amount) VALUES (100, 1, 99.00);

-- 报错！user_id = 999 在 users 表中不存在
-- INSERT INTO orders (id, user_id, amount) VALUES (101, 999, 99.00);
```

---

## PK 和 FK 的关系图解

```mermaid
erDiagram
    users ||--o{ orders : has
    users {
        int id PK        -- 主键
        string name
    }
    orders {
        int id PK        -- 主键
        int user_id FK   -- 外键，指向 users.id
        date order_date
        decimal amount
    }
```

| users 表（主表） | | orders 表（从表） |
|---|---|---|
| **id (PK)** | name | **id (PK)** | **user_id (FK)** | amount |
| 1 | 张三 | 100 | **1** | 99 |
| 2 | 李四 | 101 | **1** | 199 |
| | | 102 | **2** | 50 |

---

## 回到你的 SQL 例子

```sql
-- 你的 SQL
FROM sales_influencer_coop_project cp
JOIN sales_influencer_coop_project_influencer cpi
    ON cp.id = cpi.project_id          -- cpi.project_id 是 FK，指向 cp.id(PK)
```

| 表 | PK | FK |
|----|----|----|
| sales_influencer_coop_project | `id` | - |
| sales_influencer_coop_project_influencer | `id` | `project_id` → cp.id, `influencer_id` → si.id |
| sales_influencer_coop_project_influencer_video | `id` | `project_influencer_relation_id` → cpi.id |
| sales_influencer | `id` | - |
| data_syj_talent_video | `id` | `item_id` → cpiv.douyin_video_id（业务关联） |

---

## 快速记忆

| 概念 | 一句话理解 |
|------|-----------|
| **PK（主键）** | 就是每个人的 **身份证号**，独一无二 |
| **FK（外键）** | 就是你在别人家留的 **电话号码**，用来找到你 |

> PK = 我是谁（唯一标识自己）
> FK = 我认识谁（关联其他表）
