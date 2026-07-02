# 数据探查脚本

> 用于探查 ods_sales_sales_influencer_coop_project_influencer_video 表的数据质量

---

## 个性化修改记录

> 在此记录你对原版 SQL 的修改，方便后续追溯。
>
> | 日期 | 修改位置 | 修改内容 |
> |------|---------|--------|
> | 2026-07-02 | 2.1 重复检查 | 改为 ds >= 范围 + ORDER BY |

---

## 1. 表基本信息

```sql
-- 1.1 查看表的分区情况
SHOW PARTITIONS taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video;

-- 1.2 查看表总行数（最近分区）
SELECT COUNT(1) AS total_rows
FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624';
```

---

## 2. 重复数据检查

```sql
-- 2.1 检查 douyin_video_id 是否有重复（理论上它是主键）
-- 【原版】只查单日
SELECT douyin_video_id, COUNT(1) AS cnt
FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624'
GROUP BY douyin_video_id
HAVING COUNT(1) > 1;
```

> 💡 **我的个性化版本（2026-07-02）：** 扩大时间范围 + 排序，看哪些视频重复最多
>
> ```sql
> SELECT douyin_video_id, COUNT(1) AS cnt
> FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
> WHERE ds >= '20260501'
> GROUP BY douyin_video_id
> HAVING COUNT(1) > 1
> ORDER BY cnt DESC;
> ```

```sql
-- 2.2 查看重复的具体数据（如果有重复的话）
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY douyin_video_id ORDER BY douyin_video_id) AS rn
    FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
    WHERE ds = '20260624'
) t
WHERE rn > 1;

-- 2.3 检查 (douyin_video_id, ad_product_library_id) 组合是否有重复
SELECT douyin_video_id, ad_product_library_id, COUNT(1) AS cnt
FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624'
GROUP BY douyin_video_id, ad_product_library_id
HAVING COUNT(1) > 1;
```

---

## 3. 空值检查

```sql
-- 3.1 各字段的空值统计
SELECT
    COUNT(1) AS total_rows,
    COUNT(CASE WHEN douyin_video_id IS NULL OR douyin_video_id = '' THEN 1 END) AS null_douyin_video_id,
    COUNT(CASE WHEN ad_product_library_id IS NULL THEN 1 END) AS null_ad_product_library_id,
    COUNT(CASE WHEN project_id IS NULL THEN 1 END) AS null_project_id,
    COUNT(CASE WHEN del_flag IS NULL THEN 1 END) AS null_del_flag
FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624';

-- 3.2 查看关键字段为空的数据（用于排查问题）
SELECT *
FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624'
  AND (douyin_video_id IS NULL OR douyin_video_id = '')
  OR (ad_product_library_id IS NULL AND project_id IS NULL);
```

---

## 4. 数据分布情况

```sql
-- 4.1 del_flag 的分布
SELECT del_flag, COUNT(1) AS cnt, ROUND(COUNT(1) * 100.0 / SUM(COUNT(1)) OVER(), 2) AS ratio
FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624'
GROUP BY del_flag;

-- 4.2 ad_product_library_id 是否为空的占比
SELECT
    CASE WHEN ad_product_library_id IS NULL THEN '无广告产品' ELSE '有广告产品' END AS has_ad_product,
    COUNT(1) AS cnt,
    ROUND(COUNT(1) * 100.0 / SUM(COUNT(1)) OVER(), 2) AS ratio
FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624'
GROUP BY CASE WHEN ad_product_library_id IS NULL THEN '无广告产品' ELSE '有广告产品' END;

-- 4.3 project_id 的分布情况（TOP 10 项目）
SELECT project_id, COUNT(1) AS video_cnt
FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624'
  AND del_flag = '0'
GROUP BY project_id
ORDER BY video_cnt DESC
LIMIT 10;
```

---

## 5. 数据增量与趋势

```sql
-- 5.1 每日数据量趋势（最近7天）
SELECT ds, COUNT(1) AS daily_rows
FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds >= '20260618'
GROUP BY ds
ORDER BY ds;

-- 5.2 查看当前分区的数据范围
SELECT
    MIN(douyin_video_id) AS min_video_id,
    MAX(douyin_video_id) AS max_video_id,
    COUNT(DISTINCT project_id) AS distinct_project_cnt,
    COUNT(DISTINCT ad_product_library_id) AS distinct_ad_product_cnt
FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624'
  AND del_flag = '0';
```

---

## 6. 跨表关联验证（数据一致性）

```sql
-- 6.1 检查 project_id 是否在项目表中都存在
SELECT COUNT(1) AS orphan_records
FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video t
LEFT JOIN taidou_local_life.sales_influencer_coop_project p
    ON t.project_id = p.id
WHERE t.ds = '20260624'
  AND t.del_flag = '0'
  AND p.id IS NULL;

-- 6.2 检查 ad_product_library_id 是否在广告产品库中存在
SELECT COUNT(1) AS orphan_records
FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video t
LEFT JOIN taidou_local_life.ods_sales_sales_ad_product_library p
    ON t.ad_product_library_id = p.id
WHERE t.ds = '20260624'
  AND t.del_flag = '0'
  AND t.ad_product_library_id IS NOT NULL
  AND p.id IS NULL;
```

---

## 7. 一键探查（汇总）

```sql
-- 7.1 数据质量总览（一条 SQL 看完所有关键指标）
SELECT
    '数据量' AS check_item, COUNT(1) AS check_value
FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624'
UNION ALL
SELECT '重复视频数', COUNT(1) FROM (
    SELECT douyin_video_id FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
    WHERE ds = '20260624' GROUP BY douyin_video_id HAVING COUNT(1) > 1
) t
UNION ALL
SELECT '空视频ID数', COUNT(1) FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624' AND (douyin_video_id IS NULL OR douyin_video_id = '')
UNION ALL
SELECT '有效数据(del_flag=0)', COUNT(1) FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624' AND del_flag = '0'
UNION ALL
SELECT '已删除数据(del_flag=1)', COUNT(1) FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624' AND del_flag = '1'
UNION ALL
SELECT '无广告产品ID数', COUNT(1) FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624' AND ad_product_library_id IS NULL
UNION ALL
SELECT '无项目ID数', COUNT(1) FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
WHERE ds = '20260624' AND project_id IS NULL;
```

---

## 如何添加你的个性化修改

1. 直接在这个文件中编辑，在每条 SQL 后面添加 `> 💡 我的个性化版本` 区域
2. 或者在 `个性化修改记录` 表格中登记你的改动
3. 如果 AI 后续更新此文件，会保留 `个性化修改记录` 表格中的内容
