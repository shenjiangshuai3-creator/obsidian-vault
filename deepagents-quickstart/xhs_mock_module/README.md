# XHS Mock Module

这是一个独立的小红书仿真数据模块，用于个人学习和本地数据分析练习。

它不会修改现有 `app.py`、`data_qa_agent` 工具注册或数据库连接逻辑。你可以把它理解成一个旁路实验模块：

```text
xhs_mock_module
  -> schema
  -> mock data generator
  -> sample questions
  -> import guide
```

## 适合做什么

- 理解小红书内容、互动、账号、达人、广告、商品、订单的数据模型
- 练习 SQL 指标分析
- 给本地 LangChain / Deep Agents 智能体提供模拟数据
- 后续替换成官方 API、后台导出或手动整理的数据

## 不做什么

- 不抓取小红书真实用户数据
- 不绕过登录、反爬或风控
- 不使用 cookie 模拟接口
- 不采集隐私或非授权数据

## 目录

```text
xhs_mock_module/
  README.md
  sample_questions.md
  schema/
    mysql_schema.sql
    maxcompute_schema.sql
  scripts/
    generate_mock_data.py
  data/
    .gitkeep
```

## 生成模拟 CSV 数据

```powershell
cd C:\Users\EDY\Documents\obs\deepagents-quickstart
.\.venv\Scripts\python.exe .\xhs_mock_module\scripts\generate_mock_data.py
```

生成结果会写入：

```text
xhs_mock_module/data/
```

## 表设计

| 表名 | 说明 |
|---|---|
| `xhs_note` | 笔记基础信息 |
| `xhs_note_daily_metrics` | 笔记每日指标 |
| `xhs_account_daily_metrics` | 账号每日指标 |
| `xhs_keyword_trend` | 关键词趋势 |
| `xhs_kol_profile` | 达人画像 |
| `xhs_kol_cooperation` | 达人合作 |
| `xhs_campaign_daily_metrics` | 广告投放日报 |
| `xhs_product` | 商品 |
| `xhs_order` | 订单 |

## 推荐学习路径

1. 先看 `schema/mysql_schema.sql`，理解每张表的业务含义。
2. 运行 `generate_mock_data.py` 生成 CSV。
3. 导入 MySQL 或 MaxCompute。
4. 用智能体提问 `sample_questions.md` 里的问题。
5. 后续把模拟 CSV 替换成你自己的后台导出数据。

