---
created: 2026-07-02
tags: [SQL, ER图, 数据库设计]
---

# ER 图笔记

> 用 Mermaid 语法在 Obsidian 中绘制 ER 图

---

## 什么是 ER 图？

ER 图（Entity-Relationship Diagram）用于描述数据库表之间的关联关系。

## Mermaid ER 图语法

在 Obsidian 中，用代码块包裹以下内容即可渲染：

`mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : includes
    CUSTOMER {
        int id PK
        string name
        string email
    }
    ORDER {
        int id PK
        int customer_id FK
        date order_date
        decimal total
    }
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
    }
    PRODUCT {
        int id PK
        string name
        decimal price
    }
`

## 关系符号说明

| 符号 | 含义 |
|------|------|
| ||--o{ | 一对多（必选-可选） |
| ||--|| | 一对一（必选-必选） |
| }|--o{ | 多对多 |
| ||--o{ | 一对多（左侧必选，右侧可选） |
| o{--|| | 多对一 |
| { | 表示多端 |
| | | 表示一端 |
| o | 表示可选 |

## 示例：电商系统 ER 图

`mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER ||--o{ CART : has
    USER {
        int id PK
        string username
        string email
        string password_hash
        datetime created_at
    }
    CART ||--|{ CART_ITEM : contains
    CART {
        int id PK
        int user_id FK
        datetime created_at
    }
    CART_ITEM {
        int id PK
        int cart_id FK
        int product_id FK
        int quantity
    }
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        int id PK
        int user_id FK
        string status
        decimal total_amount
        datetime created_at
    }
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price
    }
    PRODUCT ||--o{ ORDER_ITEM : includes
    PRODUCT ||--o{ CART_ITEM : includes
    PRODUCT ||--o{ CATEGORY : belongs_to
    PRODUCT {
        int id PK
        string name
        string description
        decimal price
        int stock
    }
    CATEGORY ||--o{ PRODUCT : has
    CATEGORY {
        int id PK
        string name
        string description
    }
`

## 示例：员工-部门 ER 图

`mermaid
erDiagram
    DEPARTMENT ||--o{ EMPLOYEE : has
    EMPLOYEE ||--o{ PROJECT_EMPLOYEE : assigned_to
    PROJECT ||--o{ PROJECT_EMPLOYEE : includes
    DEPARTMENT {
        int id PK
        string name
        string manager
        string location
    }
    EMPLOYEE {
        int id PK
        string name
        int department_id FK
        string position
        date hire_date
        decimal salary
    }
    PROJECT {
        int id PK
        string name
        date start_date
        date end_date
        string status
    }
    PROJECT_EMPLOYEE {
        int employee_id FK
        int project_id FK
        string role
        int hours_worked
    }
`

## 实用技巧

1. **用 PK 标注主键，FK 标注外键**
2. **关系线放在实体定义之前**
3. **表名全大写，字段名小写**（约定俗成）
4. **可以在 ER 图下方用表格补充字段说明**

---

> 参考: https://mermaid.js.org/syntax/entityRelationshipDiagram.html
