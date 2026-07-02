---
created: 2026-07-02
tags:
  - SQL
  - ER图
  - 项目表
  - 达人
  - 爆款视频
---

# 达人项目合作 ER 图（完整版）

> 根据实际业务 SQL 梳理的表关系
> 包含：达人合作 + 爆款视频评分脚本

---

## 一、所有表清单

| # | 层级 | 表名（全称） | 别名 | 说明 |
|---|------|-------------|------|------|
| 1 | 业务层 | sales_influencer_coop_project | cp | 项目表 |
| 2 | 业务层 | sales_influencer_coop_project_influencer | cpi | 项目-达人关联表 |
| 3 | 业务层 | sales_influencer_coop_project_influencer_video | cpiv | 达人视频表 |
| 4 | 业务层 | sales_influencer | si | 达人表 |
| 5 | ODS | **ods_xd_manage_data_syj_talent_video** | **t1** | **生意经视频数据主表** |
| 6 | ODS | **ods_sales_sales_influencer_coop_project_influencer_video** | **t2** | **项目-达人-视频关联表（ODS层）** |
| 7 | ODS | **ods_sales_sales_ad_product_library** | **t3** | **广告产品库表** |
| 8 | ADS | **ads_sales_talent_video_hot_script** | **目标表** | **爆款视频热度评分结果表** |

> 注：业务层 `sales_influencer_coop_project_influencer_video` 与 ODS 层 `ods_sales_sales_influencer_coop_project_influencer_video` 是同一业务的不同分层

---

## 二、表间关系

```mermaid
erDiagram
    %% ========== 业务层关系 ==========
    sales_influencer_coop_project ||--o{ sales_influencer_coop_project_influencer : "1个项目有N个达人"
    sales_influencer_coop_project_influencer ||--o{ sales_influencer_coop_project_influencer_video : "1个关联有N个视频"
    sales_influencer_coop_project_influencer }o--|| sales_influencer : "N个达人关联1个达人信息"

    %% ========== ODS 层关系 ==========
    ods_xd_manage_data_syj_talent_video ||--o{ ods_sales_sales_influencer_coop_project_influencer_video : "item_id = douyin_video_id"
    ods_sales_sales_influencer_coop_project_influencer_video }o--|| ods_sales_sales_ad_product_library : "ad_product_library_id = id"

    %% ========== 业务层表定义 ==========
    sales_influencer_coop_project {
        int id PK
        varchar project_name
        datetime create_time
        datetime update_time
        int del_flag
    }
    sales_influencer_coop_project_influencer {
        int id PK
        int project_id FK
        int influencer_id FK
        datetime create_time
        datetime update_time
        int del_flag
    }
    sales_influencer_coop_project_influencer_video {
        int id PK
        int project_influencer_relation_id FK
        varchar douyin_video_id
        datetime create_time
        datetime update_time
        int del_flag
    }
    sales_influencer {
        int id PK
        varchar nickname
        varchar account
        varchar personal_page_url
        varchar uid
        datetime create_time
        datetime update_time
        int del_flag
    }

    %% ========== ODS 层表定义 ==========
    ods_xd_manage_data_syj_talent_video {
        int id PK
        varchar item_id
        varchar douyin_url
        varchar douyin_id
        varchar author_uid
        varchar nickname
        bigint fans_num_all
        varchar item_title
        bigint item_play_cnt
        bigint item_like_cnt
        bigint item_comment_cnt
        bigint item_pay_gmv
        varchar item_finish_play_ratio
        varchar play_5s_rate
        int item_sec
        int time_type
        datetime start_time
        datetime end_time
        datetime update_time
        string ds
    }
    ods_sales_sales_influencer_coop_project_influencer_video {
        varchar douyin_video_id PK
        int ad_product_library_id FK
        int project_id FK
        int del_flag
        string ds
    }
    ods_sales_sales_ad_product_library {
        int id PK
        int script_case_id
        int influencer_id
        varchar ai_script_content
        varchar video_path
        varchar video_cover_path
        string ds
    }
```

---

## 三、SQL 关联详解

### 3.1 核心数据流

```mermaid
graph LR
    subgraph ODS层
        A[ods_xd_manage_data<br/>_syj_talent_video]
        B[ods_sales_sales_influencer<br/>_coop_project_influencer_video]
        C[ods_sales_sales<br/>_ad_product_library]
    end
    
    subgraph ADS层
        D[ads_sales_talent_video_hot_script<br/>INSERT OVERWRITE]
    end
    
    A -- "LEFT JOIN<br/>item_id = douyin_video_id" --> B
    B -- "LEFT JOIN<br/>ad_product_library_id = id" --> C
    A -.->|数据来源| D
    C -.->|数据来源| D
```

### 3.2 第1层关联
```sql
FROM taidou_local_life.ods_xd_manage_data_syj_talent_video t1
LEFT JOIN (
    SELECT douyin_video_id,
           max(ad_product_library_id) as ad_product_library_id,
           max(project_id) as project_id
    FROM taidou_local_life.ods_sales_sales_influencer_coop_project_influencer_video
    WHERE ds >= '20260609' AND del_flag = '0'
    GROUP BY douyin_video_id
) t2 ON t1.item_id = t2.douyin_video_id
```
> **t1.item_id = t2.douyin_video_id** — 生意经视频通过 item_id 关联到项目达人视频

### 3.3 第2层关联
```sql
LEFT JOIN taidou_local_life.ods_sales_sales_ad_product_library t3
ON t2.ad_product_library_id = t3.id
AND t3.ai_script_content IS NOT NULL
AND Trim(t3.ai_script_content) <> ''
AND t3.ds >= '20260609'
```
> **t2.ad_product_library_id = t3.id** — 项目达人视频通过广告产品库ID关联广告产品信息

### 3.4 最终写入
```sql
INSERT OVERWRITE TABLE ads_sales_talent_video_hot_script PARTITION (ds='20260624')
SELECT ... FROM (...) t WHERE t.is_hot_video = '爆款'
```
> 结果写入 ADS 层，只保留爆款视频

---

## 四、爆款分层与评分

| 等级 | 播放量 | 完播率 | 5秒播放率 | 互动数 | GMV | 评分公式 |
|------|--------|--------|-----------|--------|-----|---------|
| 标杆爆款 | > 10000 | > 8% | > 8% | > 50 | > 20 | 7 + (得分/100) * 3 |
| 优质爆款 | > 5000 | > 5% | > 5% | > 30 | > 10 | 4 + (得分/100) * 2 |
| 普通爆款 | > 1000 | > 3% | > 3% | > 10 | > 0 | 1 + (得分/100) * 3 |
| 非爆款 | 不满足 | - | - | - | - | 0 |

---

## 五、标签体系

| 类别 | 标签 | 字段 | 关键词 |
|------|------|------|--------|
| 核心卖点 | 外观 | tag_sell_appearance | 外观、颜值、造型、内饰好看 |
| | 空间 | tag_sell_space | 空间、二排、小桌板、后备箱、座舱空间 |
| | 智能驾驶 | tag_sell_ad | 智能驾驶、智驾、辅助驾驶、自驾系统、逍遥智行 |
| | 续航 | tag_sell_range | 续航、插混、市区用电、长途用油、续航焦虑、三电 |
| | 品牌 | tag_sell_brand | 别克品牌、品牌故事、品牌口碑 |
| | 其他卖点 | tag_sell_other | 以上均未命中 |
| 政策权益 | 贷款 | tag_policy_loan | 免息、贷款、分期、金融礼 |
| | 置换 | tag_policy_replace | 置换、旧车置换、置换补贴 |
| | 优惠 | tag_policy_car_discount | 1000抵、下订抵扣、购车款抵扣、现金优惠 |
| | 保险 | tag_policy_insurance | 保险、车险、保险礼包 |
| | 充电 | tag_policy_charging | 充电桩、充电枪 |
| | 其他权益 | tag_policy_other | 以上均未命中 |

---

## 六、数据血缘

```mermaid
graph TD
    subgraph ODS源表
        A["ods_xd_manage_data_syj_talent_video<br/>(生意经视频)"]
        B["ods_sales_sales_influencer_coop<br/>_project_influencer_video<br/>(项目达人视频关联)"]
        C["ods_sales_sales_ad_product_library<br/>(广告产品库)"]
    end
    
    subgraph 计算过程
        D["LEFT JOIN → 爆款判定<br/>→ 热度评分 → 标签打标"]
    end
    
    subgraph ADS结果
        E["ads_sales_talent_video_hot_script<br/>(爆款视频热度评分)"]
    end
    
    A -->|item_id| D
    B -->|douyin_video_id| D
    C -->|ad_product_library_id| D
    D -->|INSERT OVERWRITE| E
```

---

> 最后更新: 2026-07-02
