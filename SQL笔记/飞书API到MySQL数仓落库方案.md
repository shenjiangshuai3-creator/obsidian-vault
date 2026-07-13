# 飞书 API 到 MySQL 数仓落库方案

## 背景

目标是通过飞书多维表格 API 拉取「主项目流程列表」中「效果通」视图的数据，写入阿里云 PolarDB/MySQL 的 `anycross` 库，并形成和 Excel 一样的横向宽表。

最终数据形态：

- 字段横向排列，字段顺序对齐 Excel 表头。
- 每条飞书记录一行。
- 字段为空时，MySQL 中写入 `NULL`。
- ODS 层保留原始 JSON 和字段清单。
- DWD 层提供业务可直接查询的宽表。

## 最终脚本

### ODS 原始落库脚本

路径：

```text
C:\Users\EDY\Documents\Codex\2026-07-08\new-chat-2\work\FINAL_AUTO_ODS_feishu_api_to_mysql_raw.sh
```

作用：

- 获取飞书 `tenant_access_token`。
- 自动读取飞书表名和视图名。
- 读取飞书字段清单。
- 调用 `records/search` 拉取记录。
- 当字段数超过飞书接口 `field_names` 单次 200 个限制时，自动分批读取并按 `record_id` 合并。
- 写入 ODS 原始记录表和字段清单表。

需要配置：

```bash
export FEISHU_APP_ID="你的飞书 APP_ID"
export FEISHU_APP_SECRET="你的飞书 APP_SECRET"
export MYSQL_PASSWORD="你的数据库密码"
```

### DWD 宽表解析脚本

路径：

```text
C:\Users\EDY\Documents\Codex\2026-07-08\new-chat-2\work\FINAL_AUTO_DWD_parse_ods_to_excel_wide.sh
```

作用：

- 自动读取飞书表名和视图名。
- 自动生成和 ODS 对应的 DWD 表名。
- 读取 ODS 原始记录表中的 `fields_json`。
- 按 Excel 的 201 个字段表头生成宽表。
- 将 JSON 字段值解析成普通列。
- 空字段写入 `NULL`。

需要配置：

```bash
export FEISHU_APP_ID="你的飞书 APP_ID"
export FEISHU_APP_SECRET="你的飞书 APP_SECRET"
export MYSQL_PASSWORD="你的数据库密码"
```

## 自动表名规则

脚本会通过飞书 API 获取：

```text
表名：主项目流程列表
视图名：效果通
```

然后生成表名后缀：

```text
mainproject_xiaoguotong
```

最终表名：

```sql
anycross.ods_feishu_mainproject_xiaoguotong_records
anycross.ods_feishu_mainproject_xiaoguotong_fields
anycross.dwd_feishu_mainproject_xiaoguotong
```

如需手动指定后缀，可在两个脚本中配置：

```bash
export FEISHU_TABLE_SLUG="mainproject"
export FEISHU_VIEW_SLUG="xiaoguotong"
```

## 最终表说明

### ODS 原始记录表

```sql
anycross.ods_feishu_mainproject_xiaoguotong_records
```

用途：

- 必须保留。
- 保存飞书接口返回的原始 records 数据。
- 后续 DWD 宽表从这张表解析。

主要字段：

```text
record_id
app_token
table_id
view_id
fields_json
raw_json
sync_time
created_at
updated_at
```

### ODS 字段清单表

```sql
anycross.ods_feishu_mainproject_xiaoguotong_fields
```

用途：

- 建议保留。
- 保存飞书多维表格字段清单。
- 用于检查字段是否完整、字段类型是什么、是否发生字段变更。
- 排查某个字段为什么没有值时很有用。

### DWD 业务宽表

```sql
anycross.dwd_feishu_mainproject_xiaoguotong
```

用途：

- 最终业务查询表。
- 结构和 Excel 一致。
- 字段横向排列。
- 每条项目数据一行。
- 空值为 `NULL`。

## 执行顺序

1. 运行 ODS 脚本：

```text
FINAL_AUTO_ODS_feishu_api_to_mysql_raw.sh
```

2. 运行 DWD 脚本：

```text
FINAL_AUTO_DWD_parse_ods_to_excel_wide.sh
```

## 验证 SQL

### 验证 ODS 原始记录

```sql
SELECT 
  record_id,
  CHAR_LENGTH(fields_json) AS fields_len,
  sync_time
FROM anycross.ods_feishu_mainproject_xiaoguotong_records
ORDER BY updated_at DESC
LIMIT 10;
```

### 验证 ODS 字段数

```sql
SELECT COUNT(1)
FROM anycross.ods_feishu_mainproject_xiaoguotong_fields;
```

预期字段数：

```text
201
```

### 验证 DWD 宽表

```sql
SELECT 
  `项目编号`,
  `项目名称`,
  `立项顺序`,
  `现归属销售`
FROM anycross.dwd_feishu_mainproject_xiaoguotong
ORDER BY `立项顺序`;
```

示例结果：

```text
V2603-SHTD-TYO-235 | 上汽通用2026Q2新媒体中心能力提升SOW | 235 | 丁晨
V2606-SHTD-TYO-315 | 2026Q3-Q4新媒体中心能力提升SOW | 315 | 丁晨
```

## 是否需要两个 ODS 表

建议保留两个 ODS 表。

必须保留：

```sql
ods_feishu_mainproject_xiaoguotong_records
```

原因：

- 它是原始数据底表。
- DWD 宽表依赖这张表解析。

建议保留：

```sql
ods_feishu_mainproject_xiaoguotong_fields
```

原因：

- 成本很低。
- 可以校验字段数是否完整。
- 可以查看字段类型和字段属性。
- 后续飞书字段变更时方便对比。

## 当前链路

```text
飞书多维表格 API
-> DataWorks Shell ODS 节点
-> MySQL ODS 原始记录表 / 字段清单表
-> DataWorks Shell DWD 节点
-> MySQL DWD Excel 同结构业务宽表
```

