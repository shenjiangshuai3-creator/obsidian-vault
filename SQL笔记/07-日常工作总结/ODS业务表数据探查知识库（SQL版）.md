# ODS业务表数据探查知识库（SQL版）

## 适用对象

- ODS层业务表
- 达人合作表
- 商品表
- 订单表
- 视频表
- 广告表

## 一、数据量检查（第一步）

### 目的

判断是否有数据、数据量是否符合预期。

```sql
SELECT COUNT(*) AS total_cnt
FROM ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds >= '20260501';
```

### 判断标准

| 现象 | 可能原因 |
| --- | --- |
| 数据量 = 0 | 同步失败 |
| 数据量突然下降 | ETL异常 |
| 数据量突然暴涨 | 重复同步 |

## 二、空值率检查（★★★★★）

### 目的

检查业务主字段是否为空。

```sql
SELECT
    COUNT(*) total_cnt,
    SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END) id_null,
    SUM(CASE WHEN project_id IS NULL THEN 1 ELSE 0 END) project_null,
    SUM(CASE WHEN influencer_id IS NULL THEN 1 ELSE 0 END) influencer_null,
    SUM(CASE WHEN video_url IS NULL THEN 1 ELSE 0 END) video_url_null,
    SUM(CASE WHEN douyin_video_id IS NULL THEN 1 ELSE 0 END) douyin_video_null,
    SUM(CASE WHEN material_id IS NULL THEN 1 ELSE 0 END) material_null,
    SUM(CASE WHEN ad_product_library_id IS NULL THEN 1 ELSE 0 END) library_null
FROM ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds >= '20260501';
```

### 判断标准

核心字段一般不能为空：

- `id`
- `project_id`
- `influencer_id`
- `douyin_video_id`

如果 `material_id` NULL率很高，需要结合业务判断是否属于回填字段。

## 三、每日数据量变化（★★★★★）

### 目的

观察同步是否稳定。

```sql
SELECT
    ds,
    COUNT(*) total_cnt
FROM ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds >= '20260501'
GROUP BY ds
ORDER BY ds;
```

### 重点观察

- 有没有突然暴涨
- 有没有突然暴跌
- 是否某天为0

## 四、每日空值率变化（★★★★★）

### 目的

检查最近是否出现回填异常。

```sql
SELECT
    ds,
    COUNT(*) total_cnt,
    SUM(CASE WHEN material_id IS NULL THEN 1 ELSE 0 END) material_null,
    ROUND(
        SUM(CASE WHEN material_id IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) null_rate
FROM ods_sales_sales_influencer_coop_project_influencer_video
GROUP BY ds
ORDER BY ds;
```

### 重点

如果最近 NULL率100%，通常表示回填任务没跑。

## 五、主键唯一性检查（★★★★★）

```sql
SELECT
    id,
    COUNT(*) cnt
FROM ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds >= '20260501'
GROUP BY id
HAVING COUNT(*) > 1;
```

正常结果：0条。

## 六、抖音视频重复检查（业务重复）

```sql
SELECT
    douyin_video_id,
    COUNT(*) cnt
FROM ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds >= '20260501'
GROUP BY douyin_video_id
HAVING COUNT(*) > 1
ORDER BY cnt DESC;
```

### 注意

这里不一定异常，可能同一个视频参与多个项目。

## 七、项目+视频重复检查

```sql
SELECT
    project_id,
    douyin_video_id,
    COUNT(*) cnt
FROM ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds >= '20260501'
  AND del_flag = 0
GROUP BY
    project_id,
    douyin_video_id
HAVING COUNT(*) > 1;
```

### 意义

检查一个项目是否重复保存视频。

## 八、达人+视频重复检查

```sql
SELECT
    influencer_id,
    douyin_video_id,
    COUNT(*) cnt
FROM ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds >= '20260501'
  AND del_flag = 0
GROUP BY
    influencer_id,
    douyin_video_id
HAVING COUNT(*) > 1;
```

### 意义

检查同一个达人是否上传重复视频。

## 九、项目+达人+视频唯一性检查（★★★★★）

这是最重要的一条规则。

```sql
SELECT
    project_id,
    influencer_id,
    douyin_video_id,
    COUNT(*) cnt
FROM ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds >= '20260501'
  AND del_flag = 0
GROUP BY
    project_id,
    influencer_id,
    douyin_video_id
HAVING COUNT(*) > 1
ORDER BY cnt DESC;
```

### 数据质量规则

对于 `del_flag = 0` 的数据，要求：

```text
project_id + influencer_id + douyin_video_id
```

必须唯一。

如果重复，基本就是重复写入。

## 十、查看重复数据详情（★★★★★）

用于定位重复原因。

```sql
SELECT
    id,
    project_id,
    influencer_id,
    douyin_video_id,
    video_url,
    material_id,
    ad_product_library_id,
    create_time,
    update_time,
    del_flag
FROM ods_sales_sales_influencer_coop_project_influencer_video
WHERE del_flag = 0
ORDER BY
    project_id,
    influencer_id,
    douyin_video_id,
    create_time;
```

如果需要只看重复数据，建议使用 `JOIN` 与重复组合结果关联（兼容 MaxCompute）。

## 十一、枚举字段检查

例如：

- `video_anchor`
- `del_flag`

```sql
SELECT
    video_anchor,
    COUNT(*)
FROM ods_sales_sales_influencer_coop_project_influencer_video
GROUP BY video_anchor;
```

检查是否出现：

- `NULL`
- `999`
- `-1`
- 其他非法值

## 十二、时间字段检查

```sql
SELECT
    MIN(create_time),
    MAX(create_time),
    MIN(update_time),
    MAX(update_time)
FROM ods_sales_sales_influencer_coop_project_influencer_video;
```

检查有没有：

- 未来时间
- 1970年
- 1900年
- 其他异常时间

## 十三、关联字段覆盖率

例如 `material_id`：

```sql
SELECT
    COUNT(*) total,
    COUNT(material_id) material_cnt,
    ROUND(
        COUNT(material_id) * 100.0 / COUNT(*),
        2
    ) coverage
FROM ods_sales_sales_influencer_coop_project_influencer_video;
```

用于分析素材回填率。

---

## 十四、抖音生意经达人视频表专项探查

### 适用表

`ods_xd_manage_data_syj_talent_video`

### 探查目标

- 判断 `20260501` 以来数据是否正常同步。
- 检查达人、视频、标题、发布时间、POI、商品等核心字段是否缺失。
- 识别 `item_id`、`item_id + time_type`、达人+视频维度的重复数据。
- 检查播放、点赞、GMV、粉丝数、视频时长等指标是否存在异常值。
- 输出播放、点赞、GMV Top 数据和播放量分层分布。

### 1. 数据规模检查

#### 总数据量

```sql
SELECT
    COUNT(*) AS total_cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501';
```

#### 每天数据量

```sql
SELECT
    ds,
    COUNT(*) AS cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501'
GROUP BY ds
ORDER BY ds;
```

#### 每天新增视频数

```sql
SELECT
    ds,
    COUNT(DISTINCT item_id) AS video_cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501'
GROUP BY ds
ORDER BY ds;
```

### 2. 核心字段空值检查

```sql
SELECT
    COUNT(*) AS total_cnt,
    SUM(CASE WHEN item_id IS NULL THEN 1 ELSE 0 END) AS item_id_null,
    SUM(CASE WHEN douyin_id IS NULL THEN 1 ELSE 0 END) AS douyin_id_null,
    SUM(CASE WHEN nickname IS NULL THEN 1 ELSE 0 END) AS nickname_null,
    SUM(CASE WHEN item_title IS NULL THEN 1 ELSE 0 END) AS title_null,
    SUM(CASE WHEN item_create_ts IS NULL THEN 1 ELSE 0 END) AS create_ts_null,
    SUM(CASE WHEN publish_type IS NULL THEN 1 ELSE 0 END) AS publish_type_null,
    SUM(CASE WHEN poi_id IS NULL THEN 1 ELSE 0 END) AS poi_null,
    SUM(CASE WHEN top1_product_id IS NULL THEN 1 ELSE 0 END) AS top1_product_null
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501';
```

重点关注字段：

- `item_id`：视频唯一标识，原则上不能为空。
- `douyin_id`：达人抖音号，达人分析核心字段。
- `nickname`：达人昵称，用于报表展示和人工核验。
- `item_title`：视频标题，用于内容分析。
- `item_create_ts`：视频发布时间，用于时间维度分析。
- `poi_id`：本地生活场景关联字段，允许为空但需看业务覆盖率。
- `top1_product_id`：商品关联字段，空值率高时需确认是否为非带货视频。

### 3. 重复数据检查

#### `item_id` 是否重复

```sql
SELECT
    item_id,
    COUNT(*) AS cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501'
GROUP BY item_id
HAVING COUNT(*) > 1
ORDER BY cnt DESC;
```

#### `item_id + time_type` 是否重复

```sql
SELECT
    item_id,
    time_type,
    COUNT(*) AS cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501'
GROUP BY item_id, time_type
HAVING COUNT(*) > 1;
```

#### 达人+视频是否重复

```sql
SELECT
    douyin_id,
    item_id,
    COUNT(*) AS cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501'
GROUP BY douyin_id, item_id
HAVING COUNT(*) > 1;
```

### 4. 枚举字段检查

```sql
SELECT publish_type, COUNT(*) AS cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501'
GROUP BY publish_type;

SELECT author_type, COUNT(*) AS cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501'
GROUP BY author_type;

SELECT time_type, COUNT(*) AS cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501'
GROUP BY time_type;
```

检查是否出现异常枚举值，例如 `NULL`、`-1`、`999` 或业务未定义值。

### 5. 指标异常值检查

```sql
SELECT * FROM ods_xd_manage_data_syj_talent_video WHERE item_play_cnt < 0;
SELECT * FROM ods_xd_manage_data_syj_talent_video WHERE item_like_cnt < 0;
SELECT * FROM ods_xd_manage_data_syj_talent_video WHERE item_pay_gmv < 0;
SELECT * FROM ods_xd_manage_data_syj_talent_video WHERE fans_num_all < 0;
SELECT * FROM ods_xd_manage_data_syj_talent_video WHERE item_sec <= 0 OR item_sec > 3600;
```

判断标准：

- 播放、点赞、GMV、粉丝数不应为负数。
- `item_sec <= 0` 通常异常。
- `item_sec > 3600` 需要结合抖音视频业务规则判断是否合理。

### 6. 业务统计

#### 达人数

```sql
SELECT COUNT(DISTINCT douyin_id) AS author_cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501';
```

#### 视频数

```sql
SELECT COUNT(DISTINCT item_id) AS video_cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501';
```

#### 平均播放量

```sql
SELECT AVG(item_play_cnt) AS avg_play_cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501';
```

#### 播放 Top 10

```sql
SELECT item_id, nickname, item_title, item_play_cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501'
ORDER BY item_play_cnt DESC
LIMIT 10;
```

#### 点赞 Top 10

```sql
SELECT item_id, nickname, item_title, item_like_cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501'
ORDER BY item_like_cnt DESC
LIMIT 10;
```

#### GMV Top 10

```sql
SELECT item_id, nickname, item_title, item_pay_gmv
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501'
ORDER BY item_pay_gmv DESC
LIMIT 10;
```

### 7. 播放量分层分布

```sql
SELECT
    CASE
        WHEN item_play_cnt < 1000 THEN '<1k'
        WHEN item_play_cnt < 10000 THEN '1k-1w'
        WHEN item_play_cnt < 100000 THEN '1w-10w'
        WHEN item_play_cnt < 1000000 THEN '10w-100w'
        ELSE '100w+'
    END AS play_level,
    COUNT(*) AS cnt
FROM ods_xd_manage_data_syj_talent_video
WHERE ds >= '20260501'
GROUP BY
    CASE
        WHEN item_play_cnt < 1000 THEN '<1k'
        WHEN item_play_cnt < 10000 THEN '1k-1w'
        WHEN item_play_cnt < 100000 THEN '1w-10w'
        WHEN item_play_cnt < 1000000 THEN '10w-100w'
        ELSE '100w+'
    END
ORDER BY cnt DESC;
```

### 探查结论记录模板

```text
表名：ods_xd_manage_data_syj_talent_video
探查时间：YYYY-MM-DD
数据范围：ds >= '20260501'

1. 数据规模：
   - 总数据量：
   - 日数据量是否稳定：
   - 每日新增视频数是否异常：

2. 空值情况：
   - 核心字段是否存在空值：
   - POI / 商品字段空值是否符合业务预期：

3. 重复情况：
   - item_id 是否重复：
   - item_id + time_type 是否重复：
   - 达人+视频是否重复：

4. 枚举和异常值：
   - publish_type / author_type / time_type 是否正常：
   - 是否存在负数指标或异常视频时长：

5. 业务统计：
   - 达人数：
   - 视频数：
   - Top 视频是否合理：

6. 处理建议：
   - 是否需要补数：
   - 是否需要去重：
   - 是否需要和业务确认字段含义：
```