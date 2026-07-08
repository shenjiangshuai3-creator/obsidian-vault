# dws_local_life_trade_marketing_wide_di 设计草案

## 1. 建设目标

建设一张跨主题域的本地生活交易营销宽表，打通订单/核销、投放、门店/POI、达人、视频/内容等数据，用于分析本地生活成交、核销、退款、投放转化、达人内容贡献和门店经营效果。

目标表建议命名：`dws_local_life_trade_marketing_wide_di`

建议分区：`ds`

建议更新方式：按日分区覆盖写入，保留订单最新状态。当前项目内所有分区字段统一使用 `ds`，不使用 `dt`。

## 1.1 已知 DML 口径修正

根据已提供的 DML，`dwd_data_life_douyin_trade_verify_order_poi` 已经是由 4 张 ODS 表按 `order_id` 左关联形成的 DWD 宽表：

```text
ods_data_life_douyin_trade_detail t1
  left join ods_data_life_douyin_verify_detail t2 on t1.order_id = t2.order_id and t2.ds >= '20260501'
  left join ods_data_local_ads_order_detail t3 on t1.order_id = t3.order_id and t3.ds >= '20260501'
  left join ods_data_local_ads_poi_order_detail t4 on t1.order_id = t4.order_id and t4.ds >= '20260501'
where t1.ds >= '20260501'
```

因此 V1 宽表不建议再从 4 张 ODS 重复起宽，而是优先复用该 DWD 表作为主事实表，在其基础上补充达人、视频、素材、脚本、直播等跨主题域属性。

另一个已知 DML 表明 `dwd_union_ads_order_poi_order_detail` 当前主要沉淀本地投放与门店全域成单 `order_id` 集合，可用于圈选/校验投放成单订单，但字段粒度较窄，不应作为主宽表事实表。

## 1.2 MaxCompute 元数据探查结论

已通过 PyODPS 读取核心表元数据，确认以下结论：

1. 核心表分区字段均为 `ds`。
2. `dwd_data_life_douyin_trade_verify_order_poi` 已包含订单、核销、标准投放、门店全域、达人昵称/UID、内容地址等字段，可作为 V1 主事实表。
3. `ods_data_xt_author_base_info` 的达人名称和粉丝字段真实字段为 `nick_name`、`follower`，不是 `author_name`、`author_fans_cnt`。
4. `ods_data_xt_author_video_metrics` 是达人传播价值指标表，粒度偏达人 + 日期类型，不是单视频明细表；真实字段包括 `author_id`、`avg_duration`、`comment_avg`、`like_avg`、`share_avg`、`item_num` 等。
5. `ods_data_local_ads_material` 是标准投放素材级指标表，可按 `adv_id + promotion_id + stat_time_day` 聚合后补充消耗、曝光、点击、转化、素材互动、短视频成交等指标。
6. `dws_sales_talent_video_script_detail` 是单条视频指标与 AI 脚本明细表，真实视频字段为 `item_id`、`douyin_url`、`douyin_id`、`author_uid`、`nickname`、`item_title`、`ai_script_content`。

## 1.3 第二批 MaxCompute 元数据探查结论

已继续读取第二批 10 张表元数据，确认以下结论：

1. 第二批表分区字段同样均为 `ds`。
2. `dwd_union_ads_order_poi_order_detail` 只有 `order_id` 和 `ds` 两个字段，适合作为“投放成单订单集合”进行圈选/校验，不适合作为宽表主事实或补充维度来源。
3. `ods_data_life_douyin_trade_detail` 与 DWD 主表订单字段高度一致，是 DWD 的订单明细来源，可用于对账和补充订单字段。
4. `ods_data_life_douyin_verify_detail` 是核销明细来源，包含 `verify_record_id`、`coupon_code`、`verify_store_id`、`verify_store_name`、`verify_time`、`hx_card_verify_amount`、`coupon_user_actual_pay` 等券/核销粒度字段。
5. `ods_data_local_ads_order_detail` 是标准投放成单明细，仅包含 `adv_id`、`cdp_promotion_id`、`cdp_promotion_name`、`order_id`、`pay_order_date/time`、`oto_pay_order_amount` 等字段。
6. `ods_data_local_ads_poi_order_detail` 是门店全域成单明细，关键字段为 `adv_id`、`ad_id`、`ad_info_name`、`order_id`、`assist_aid`、`oto_pay_order_amount`。
7. `ods_data_local_ads_project_stats` 与 `ods_data_local_ads_promotion_detail` 分别是标准投放项目级/单元级日指标表，可补充消耗、曝光、点击、转化、短视频成交、直播成交、POI 浏览等指标。
8. `ods_data_xt_author_credit_data` 可补充达人履约能力，字段包括 `author_id`、`credit_score`、`new_credit_score`、`order_cnt`、`process_order_cnt`、`max_process_order_cnt`。
9. `ods_xd_manage_data_local_ads_live_material_detail` 是直播全域投放素材明细，关键字段为 `adv_id`、`room_id`、`room_title`、`stat_time_day`、`record_time` 以及直播消耗/成交/观看/互动指标。
10. `ods_data_syj_live` 是生意经直播间经营指标，关键字段为 `douyin_id`、`room_id`、`room_name`、`live_start_time`、`live_end_time`、`gmv`、`room_verify_order_amt_td`、`room_refund_order_amt_td`、`poi_account_id` 等。

## 1.4 第三批 MaxCompute 元数据探查结论

已继续读取第三批 10 张表元数据，确认以下结论：

1. 第三批表分区字段同样均为 `ds`。
2. `ods_data_linke_author_wide` 是抖音林客达人全维度宽表，关键字段为 `uid`、`unique_id`、`nick_name`、`douyin_id`、`fans_count`、`local_fans_count`、`talent_item_gmv_digit_value`、`talent_item_order_cnt_digit_value`、`verify_rate_30d_statistice_value_value` 等，可作为达人 V2 增强来源。
3. `ods_data_xt_author_latest_video` 是巨量星图作者最新视频表，关键字段为 `author_id`、`item_id`、`video_id`、`core_user_id`、`item_title`、`item_date`，适合补充“达人最近视频”维度，不直接承载交易指标。
4. `ods_data_local_ads_poi_ad_stats` 是门店全域单元级投放指标表，关键字段为 `adv_id`、`ad_id`、`ad_info_name`、`stat_time_day`、`video_stat_cost_for_roi2`、`video_oto_pay_order_stat_amount_for_roi2`、`video_oto_pay_order_count_for_roi2`、`video_oto_pay_order_roi2_new` 等。
5. `ods_conf_brand_store_address` 是品牌全国门店地址表，包含 `org_id`、`nickname`、`province`、`city`、`address`，可用于品牌门店地址补充，但缺少与抖音核销门店稳定映射字段。
6. `ods_conf_store` / `ods_conf_store_0411` 是内部门店配置表，包含 `id`、`org_id`、`ocean_org_id`、`address`、`room_id`、`province_id`、`city_id`、`brand_name`，可用于内部门店/直播房间号补充。
7. `ods_data_douyin_dealer_manage_list` 是巨懂车经销商列表，包含懂车帝经销商 ID、企业主抖音 UID/昵称/抖音号、省市、地址、主机厂经销商 ID/名称等，更偏汽车经销商维度。
8. `ods_dealer_store` 是经销商门店维表，包含 `id`、`brand_id`、`region_id`、`store_name`、`store_code`、`province_id`、`city_id`、`city_name`、`store_level`、`store_status` 等。
9. `ods_dealer_store_account` 是门店账户表，包含 `dealer_store_account_id`、`store_id`、`account_name`，可从账户映射到经销商门店。
10. `ods_brand_detail` 是品牌维表，包含 `brand_id`、`brand_name`、`brand_status`，可通过 `ods_dealer_store.brand_id` 补充品牌属性。

## 2. 业务问题

该宽表优先支撑以下分析：

- 本地生活订单来自哪个投放项目、投放单元、门店/POI。
- 成交、核销、退款、GMV、实付金额、核销金额等交易指标分析。
- 标准投放与门店全域投放的成交和核销效果对比。
- 达人、视频、素材对本地生活交易的贡献分析。
- 门店、城市、品牌、经销商维度的成交与履约表现分析。

## 3. 主题域覆盖

| 主题域 | 作用 | 代表表 |
|---|---|---|
| 订单交易 | 主事实链路，提供订单、核销、退款和金额字段 | `dwd_data_life_douyin_trade_verify_order_poi`, `ods_data_life_douyin_trade_detail`, `ods_data_life_douyin_verify_detail` |
| 广告/投放 | 补充投放计划、项目、单元、消耗、曝光、点击等字段 | `ods_data_local_ads_project_stats`, `ods_data_local_ads_promotion_detail`, `ods_data_local_ads_poi_ad_stats` |
| 门店/POI | 补充 POI、门店、经销商、城市、品牌等属性 | `dwd_union_ads_order_poi_order_detail`, `ods_data_local_ads_poi_order_detail`, `ods_conf_store`, `ods_dealer_store`, `ods_brand_detail` |
| 达人/作者 | 补充达人基础信息、达人信用和履约能力 | `ods_data_xt_author_base_info`, `ods_data_xt_author_credit_data`, `ods_data_linke_author_wide` |
| 视频/内容/素材 | 补充视频、素材、脚本、内容表现指标 | `ods_data_local_ads_material`, `ods_data_xt_author_video_metrics`, `dws_sales_talent_video_script_detail` |
| 直播 | 二期扩展，用于直播间带来的本地生活成交归因 | `ods_xd_manage_data_local_ads_live_material_detail`, `ods_data_syj_live` |

## 4. 推荐粒度

第一版推荐采用“订单/核销明细粒度”。

建议唯一键优先级：

1. `order_id + verify_record_id + verify_store_id + ds`
2. 如果没有核销单号，使用 `order_id + verify_store_id + ds`
3. 如果订单与投放明细存在一对多，需要先在投放侧按订单粒度聚合或取最新记录，避免宽表金额重复。

不建议第一版直接做“门店-日期”或“达人-视频-日期”粒度，因为会丢失订单明细和核销链路，后续可以基于这张明细宽表再派生汇总表。

## 5. 依赖表分层

### 5.1 主事实表

| 表名 | 角色 | 当前说明 |
|---|---|---|
| `dwd_data_life_douyin_trade_verify_order_poi` | 首选主表 | 订单大宽表，包含成交明细、核销、投放、POI 信息 |
| `ods_data_life_douyin_trade_detail` | 订单明细补充 | 抖音来客成交明细 |
| `ods_data_life_douyin_verify_detail` | 核销明细补充 | 抖音来客核销明细 |
| `ods_ord_laike_trade_detail` | 备选订单来源 | 当前无说明，需要字段探查后确认是否可用 |

第一版建议优先以 `dwd_data_life_douyin_trade_verify_order_poi` 作为主表。如果该表字段已经覆盖订单、核销、POI、投放信息，则 ODS 明细只作为校验和补字段来源。

### 5.2 投放事实表

| 表名 | 角色 | 当前说明 |
|---|---|---|
| `ods_data_local_ads_order_detail` | 标准投放成单明细 | 本地推标准投放单元级成单明细 |
| `ods_data_local_ads_poi_order_detail` | 门店全域成单明细 | 本地推门店全域单元级成单明细 |
| `ods_data_local_ads_project_stats` | 项目级投放指标 | 标准投放项目级数据明细 |
| `ods_data_local_ads_promotion_detail` | 单元级投放指标 | 标准投放单元级投放明细 |
| `ods_data_local_ads_poi_ad_stats` | 门店全域投放指标 | 门店全域单元级投放明细 |
| `dwd_union_ads_order_poi_order_detail` | 投放与门店全域成单汇总 | 可作为订单投放归因校验表 |

### 5.2.1 门店全域投放指标补充

| 表名 | 角色 | 当前说明 |
|---|---|---|
| `ods_data_local_ads_poi_ad_stats` | 门店全域单元级投放指标 | 按 `adv_id + ad_id + stat_time_day` 聚合/关联，可补充全域消耗、成交金额、成交订单数、ROI、券助力成交等指标 |

### 5.3 达人与内容维表/事实表

| 表名 | 角色 | 当前说明 |
|---|---|---|
| `ods_data_xt_author_base_info` | 达人基础维表 | 巨量星图达人主信息 |
| `ods_data_xt_author_credit_data` | 达人履约/订单能力 | 达人信用分与订单能力数据 |
| `ods_data_linke_author_wide` | 林客达人宽表 | 抖音林客达人五表合一 |
| `ods_data_xt_author_video_metrics` | 达人传播价值指标 | 达人级近 30/90 天传播能力，不是单视频粒度 |
| `ods_data_xt_author_latest_video` | 作者最新视频 | 最新视频表现 |
| `ods_data_local_ads_material` | 投放素材明细 | 标准投放素材级数据明细 |
| `dws_sales_talent_video_script_detail` | 达人视频脚本明细 | 单条视频指标与 AI 脚本明细 |

### 5.3.1 门店/经销商/品牌维表

| 表名 | 角色 | 当前说明 |
|---|---|---|
| `ods_conf_brand_store_address` | 品牌门店地址 | 只有品牌组织、门店昵称、省市地址，缺少稳定抖音 POI ID |
| `ods_conf_store` | 内部门店配置 | 有内部门店 ID、组织 ID、巨量组织 ID、直播房间号、省市、品牌名 |
| `ods_data_douyin_dealer_manage_list` | 抖音/懂车帝经销商管理 | 有企业主抖音 UID/抖音号、经销商 ID、经销商名称、省市地址 |
| `ods_dealer_store` | 经销商门店维表 | 有门店 ID、品牌 ID、门店名称、城市、门店等级和状态 |
| `ods_dealer_store_account` | 经销商门店账户 | 可通过 `store_id` 关联门店，并提供账户 ID/名称 |
| `ods_brand_detail` | 品牌维表 | 可通过 `brand_id` 补充品牌名称和状态 |

### 5.4 直播与二期扩展表

| 表名 | 角色 | 当前说明 |
|---|---|---|
| `ods_xd_manage_data_local_ads_live_material_detail` | 直播全域投放素材明细 | 直播投放消耗、成交、观看、互动指标，粒度偏直播间 + 统计时间 |
| `ods_data_syj_live` | 生意经直播间经营指标 | 直播间 GMV、成交人数、核销、退款、曝光、观看、门店账号等指标 |

## 6. 字段设计

字段名需要读取 MaxCompute 元数据后落成真实字段。以下是逻辑字段草案。

### 6.1 技术字段

| 字段 | 类型建议 | 说明 |
|---|---|---|
| `ds` | string | 分区日期，格式 `yyyyMMdd` |
| `etl_time` | datetime | 写入时间 |
| `source_table_flags` | string | 命中的来源表标记，便于追溯 |

### 6.2 订单与核销字段

| 字段 | 类型建议 | 说明 |
|---|---|---|
| `order_id` | string | 订单 ID |
| `verify_record_id` | string | 核销记录 ID，对应 DWD 中 `verify_record_id` |
| `order_status` | string | 订单状态 |
| `verify_status` | string | 核销状态 |
| `refund_status` | string | 退款状态 |
| `order_create_time` | datetime | 下单时间 |
| `pay_time` | datetime | 支付时间 |
| `verify_time` | datetime | 核销时间 |
| `refund_time` | datetime | 退款时间 |
| `product_id` | string | 商品/团购商品 ID |
| `product_name` | string | 商品名称 |
| `sku_id` | string | SKU ID |
| `sku_name` | string | SKU 名称 |

### 6.3 门店/POI 字段

| 字段 | 类型建议 | 说明 |
|---|---|---|
| `verify_store_id` | string | 核销门店 ID，对应 DWD 中 `verify_store_id` |
| `poi_name` | string | POI 名称 |
| `store_id` | string | 内部门店 ID |
| `store_name` | string | 门店名称 |
| `merchant_id` | string | 商家 ID |
| `merchant_name` | string | 商家名称 |
| `brand_id` | string | 品牌 ID |
| `brand_name` | string | 品牌名称 |
| `city_id` | string | 城市 ID |
| `city_name` | string | 城市名称 |
| `province_name` | string | 省份 |

### 6.4 投放字段

| 字段 | 类型建议 | 说明 |
|---|---|---|
| `ad_platform` | string | 投放平台，如本地推/巨量本地推 |
| `ad_scene` | string | 投放场景，标准投放/门店全域/直播全域 |
| `project_id` | string | 投放项目 ID |
| `project_name` | string | 投放项目名称 |
| `promotion_id` | string | 投放单元 ID |
| `promotion_name` | string | 投放单元名称 |
| `advertiser_id` | string | 广告主 ID |
| `material_id` | string | 素材 ID |
| `campaign_id` | string | 计划 ID，如源表存在 |

### 6.5 达人与内容字段

| 字段 | 类型建议 | 说明 |
|---|---|---|
| `author_id` | string | 达人/作者 ID |
| `author_name` | string | 达人/作者名称，来源 `ods_data_xt_author_base_info.nick_name` 或脚本表 `nickname` |
| `author_level` | string | 达人等级 |
| `author_fans_cnt` | bigint | 粉丝数，来源 `ods_data_xt_author_base_info.follower` 或脚本表 `fans_num_all` |
| `author_credit_score` | decimal(18,4) | 达人信用/履约评分 |
| `author_new_credit_score` | bigint | 新信用分，来源 `ods_data_xt_author_credit_data.new_credit_score` |
| `author_order_cnt` | string | 达人总订单数，来源 `ods_data_xt_author_credit_data.order_cnt` |
| `author_process_order_cnt` | string | 达人进行中订单数，来源 `ods_data_xt_author_credit_data.process_order_cnt` |
| `author_max_process_order_cnt` | string | 达人最大可接订单数，来源 `ods_data_xt_author_credit_data.max_process_order_cnt` |
| `linke_uid` | string | 林客达人 UID，来源 `ods_data_linke_author_wide.uid` |
| `linke_local_fans_count` | string | 林客本地粉丝数 |
| `linke_item_gmv` | decimal(38,18) | 林客视频总 GMV |
| `linke_item_order_cnt` | bigint | 林客视频总订单数 |
| `linke_verify_rate_30d` | string | 林客 30 日核销率 |
| `video_id` | string | 视频 ID，来源 `dws_sales_talent_video_script_detail.item_id` |
| `video_title` | string | 视频标题，来源 `item_title` |
| `video_publish_time` | string | 发布时间，来源 `item_create_ts` |
| `script_id` | string | AI 脚本 ID |
| `script_content` | string | 脚本内容摘要，来源 `ai_script_content` |
| `material_type` | string | 素材类型 |

### 6.6 指标字段

| 字段 | 类型建议 | 说明 |
|---|---|---|
| `order_cnt` | bigint | 订单数，明细粒度通常为 1 |
| `pay_amount` | decimal(18,2) | 支付金额 |
| `gmv_amount` | decimal(18,2) | GMV |
| `verify_amount` | decimal(18,2) | 核销金额 |
| `refund_amount` | decimal(18,2) | 退款金额 |
| `coupon_amount` | decimal(18,2) | 优惠金额 |
| `ad_cost` | decimal(18,2) | 广告消耗 |
| `show_cnt` | bigint | 曝光次数 |
| `click_cnt` | bigint | 点击次数 |
| `convert_cnt` | bigint | 转化次数 |
| `video_play_cnt` | bigint | 视频播放数 |
| `video_like_cnt` | bigint | 视频点赞数 |
| `video_comment_cnt` | bigint | 视频评论数 |
| `video_share_cnt` | bigint | 视频分享数 |
| `project_stat_cost` | decimal(38,18) | 项目级消耗 |
| `promotion_stat_cost` | decimal(38,18) | 单元级消耗 |
| `promotion_oto_pay_order_count` | bigint | 单元级成交订单数 |
| `promotion_oto_pay_order_amount` | decimal(38,18) | 单元级成交金额 |
| `promotion_live_oto_pay_order_count` | bigint | 单元级直播成交订单数 |
| `promotion_live_oto_pay_order_amount` | decimal(38,18) | 单元级直播成交金额 |
| `poi_ad_cost` | decimal(38,18) | 门店全域投放消耗 |
| `poi_ad_pay_order_count` | bigint | 门店全域成交订单数 |
| `poi_ad_pay_order_amount` | decimal(38,18) | 门店全域成交金额 |
| `poi_ad_roi` | decimal(38,18) | 门店全域支付 ROI |
| `live_room_id` | string | 直播间 ID |
| `live_room_name` | string | 直播间名称 |
| `live_gmv` | decimal(38,18) | 直播间成交金额 |
| `live_verify_amount` | decimal(38,18) | 直播间核销金额 |
| `live_refund_amount` | decimal(38,18) | 直播间退款金额 |

## 7. Join 设计

### 7.1 主链路

```text
订单/核销主表
  left join 标准投放成单明细
  left join 门店全域成单明细
  left join 投放项目/单元指标
  left join POI/门店属性
  left join 达人基础信息
  left join 达人视频/素材指标
```

### 7.2 Join Key 候选

实际 Join Key 必须以字段探查为准。候选如下：

| 连接对象 | 候选 Join Key | 风险 |
|---|---|---|
| 订单明细 + 核销明细 | `order_id`, `verify_record_id` | 一单多券、一券多次核销要确认 |
| 订单 + 标准投放成单 | `order_id`, `cdp_promotion_id`, `adv_id` | DWD 已通过 `order_id` 接入 t3，后续只需补属性 |
| 订单 + 门店全域成单 | `order_id`, `ad_id`, `adv_id` | DWD 已通过 `order_id` 接入 t4，需防止标准投放与门店全域重复归因 |
| 订单 + POI/门店 | `verify_store_id`, `verify_store_name` | 名称 Join 不稳定，优先 ID |
| 投放 + 素材 | `material_id`, `promotion_id`, `project_id` | 一个单元多素材会放大订单金额 |
| 素材 + 视频 | `video_id`, `material_id` | 素材与视频可能不是一一对应 |
| 达人基础 + 主表 | `talent_uid = author_id` 或 `talent_douyin_id = unique_id` | 巨量星图 ID 与抖音 UID/抖音号可能不是同一体系，需样例值校验 |
| 脚本视频 + 主表 | `content_url = douyin_url` 或 `talent_uid = author_uid` | `content_url` 可能是 URL，不一定是视频 ID；优先 URL 精确匹配 |
| 素材指标 + 主表 | `adv_id`, `cdp_promotion_id = promotion_id`, `ds/stat_time_day` | 素材侧一单元多素材，必须先聚合到单元日粒度 |
| 达人信用 + 达人基础 | `author_id` | 信用表 `author_id` 为星图/林客 user_core_id，需与主表达人 UID 抽样比对 |
| 项目指标 + 主表 | `adv_id`, `project_id`, `stat_time_day` | 主表暂不直接携带项目 ID，可通过单元/素材表补齐后再接 |
| 单元指标 + 主表 | `adv_id`, `cdp_promotion_id`, `stat_time_day` | 与标准投放成单字段同名，适合补充单元日指标 |
| 门店全域指标 + 主表 | `adv_id`, `ad_id`, `stat_time_day` | 来源 `ods_data_local_ads_poi_ad_stats`，适合补充门店全域消耗/成交/ROI |
| 林客达人宽表 + 主表 | `talent_uid = uid` 或 `talent_douyin_id = douyin_id/unique_id` | 林客 UID、星图 author_id、抖音号可能不是同一体系，必须抽样验证 |
| 最新视频 + 达人 | `author_id` | 只用于补充最近视频，不应直接按达人关联到订单导致一单多视频放大 |
| 经销商门店 + 品牌 | `ods_dealer_store.brand_id = ods_brand_detail.brand_id` | 品牌维度内部链路稳定，但与抖音核销门店仍需映射 |
| 内部门店 + 直播 | `ods_conf_store.room_id = room_id` | 可用于直播房间号补门店，但只适用于已维护 room_id 的门店 |
| 直播投放 + 主表 | `adv_id`, `room_id`, `stat_time_day` | 主表缺少 `room_id`，需通过内容 URL/直播间素材或投放链路进一步归因 |
| 生意经直播 + 主表 | `douyin_id`, `room_id`, `ds` | 更适合作为直播间维度汇总补充，直接订单归因较弱 |

## 8. SQL 骨架

```sql
INSERT OVERWRITE TABLE dws_local_life_trade_marketing_wide_di PARTITION (ds >= '20260501')
WITH trade_base AS (
    SELECT
        /* 字段来自已提供 DML 生成的 DWD 表 */
        order_id,
        merchant_order_no,
        order_tag,
        order_status,
        after_sale_flag,
        place_order_time,
        pay_time,
        product_name,
        product_id,
        quantity,
        customer_actual_pay,
        order_actual_receipt,
        total_refund_amount,
        refund_amount,
        verification_status,
        verification_time,
        verify_record_id,
        verify_province,
        verify_city,
        verify_store_id,
        verify_store_name,
        verify_status,
        verify_time,
        adv_id,
        cdp_promotion_id,
        cdp_promotion_name,
        cdp_marketing_goal,
        oto_pay_order_amount,
        ad_id,
        ad_info_name,
        content_url,
        talent_nickname,
        talent_douyin_id,
        talent_uid,
        promoter_name,
        transaction_channel
    FROM dwd_data_life_douyin_trade_verify_order_poi
    WHERE ds >= '20260501'
),
author_dim AS (
    SELECT
        author_id,
        MAX(unique_id) AS author_unique_id,
        MAX(nick_name) AS author_name,
        MAX(grade) AS author_level,
        MAX(follower) AS author_fans_cnt,
        MAX(avg_play) AS author_avg_play
    FROM ods_data_xt_author_base_info
    WHERE ds >= '20260501'
    GROUP BY author_id
),
author_video_metric AS (
    SELECT
        author_id,
        MAX(CASE WHEN date_type = '2' THEN avg_duration END) AS avg_duration_30d,
        MAX(CASE WHEN date_type = '2' THEN comment_avg END) AS comment_avg_30d,
        MAX(CASE WHEN date_type = '2' THEN like_avg END) AS like_avg_30d,
        MAX(CASE WHEN date_type = '2' THEN share_avg END) AS share_avg_30d,
        MAX(CASE WHEN date_type = '2' THEN item_num END) AS item_num_30d,
        MAX(CASE WHEN date_type = '3' THEN avg_duration END) AS avg_duration_90d,
        MAX(CASE WHEN date_type = '3' THEN comment_avg END) AS comment_avg_90d,
        MAX(CASE WHEN date_type = '3' THEN like_avg END) AS like_avg_90d,
        MAX(CASE WHEN date_type = '3' THEN share_avg END) AS share_avg_90d,
        MAX(CASE WHEN date_type = '3' THEN item_num END) AS item_num_90d
    FROM ods_data_xt_author_video_metrics
    WHERE ds >= '20260501'
    GROUP BY author_id
),
author_credit AS (
    SELECT
        author_id,
        MAX(credit_score) AS author_credit_score,
        MAX(new_credit_score) AS author_new_credit_score,
        MAX(order_cnt) AS author_order_cnt,
        MAX(process_order_cnt) AS author_process_order_cnt,
        MAX(max_process_order_cnt) AS author_max_process_order_cnt
    FROM ods_data_xt_author_credit_data
    WHERE ds >= '20260501'
    GROUP BY author_id
),
linke_author AS (
    SELECT
        uid AS linke_uid,
        MAX(unique_id) AS linke_unique_id,
        MAX(douyin_id) AS linke_douyin_id,
        MAX(nick_name) AS linke_nick_name,
        MAX(city_name) AS linke_city_name,
        MAX(fans_count) AS linke_fans_count,
        MAX(local_fans_count) AS linke_local_fans_count,
        MAX(talent_item_gmv_digit_value) AS linke_item_gmv,
        MAX(talent_item_order_cnt_digit_value) AS linke_item_order_cnt,
        MAX(verify_rate_30d_statistice_value_value) AS linke_verify_rate_30d
    FROM ods_data_linke_author_wide
    WHERE ds >= '20260501'
    GROUP BY uid
),
latest_video AS (
    SELECT
        author_id,
        MAX(item_id) AS latest_item_id,
        MAX(video_id) AS latest_video_file_id,
        MAX(item_title) AS latest_video_title,
        MAX(item_date) AS latest_video_date
    FROM ods_data_xt_author_latest_video
    WHERE ds >= '20260501'
    GROUP BY author_id
),
material_metric AS (
    SELECT
        adv_id,
        promotion_id,
        MAX(project_id) AS project_id,
        MAX(project_name) AS project_name,
        MAX(promotion_name) AS promotion_name,
        COUNT(DISTINCT material_id) AS material_cnt,
        SUM(stat_cost) AS ad_cost,
        SUM(show_cnt) AS show_cnt,
        SUM(click_cnt) AS click_cnt,
        SUM(convert_cnt) AS convert_cnt,
        SUM(play_cnt) AS video_play_cnt,
        SUM(like_cnt) AS video_like_cnt,
        SUM(comment_cnt) AS video_comment_cnt,
        SUM(share_cnt) AS video_share_cnt,
        SUM(oto_pay_order_count) AS material_pay_order_cnt,
        SUM(oto_pay_order_amount) AS material_pay_order_amount
    FROM ods_data_local_ads_material
    WHERE ds >= '20260501'
      AND stat_time_day = '${bizdate}'
    GROUP BY adv_id, promotion_id
),
promotion_metric AS (
    SELECT
        adv_id,
        cdp_project_id,
        MAX(cdp_project_name) AS cdp_project_name,
        cdp_promotion_id,
        MAX(cdp_promotion_name) AS cdp_promotion_name,
        SUM(stat_cost) AS promotion_stat_cost,
        SUM(show_cnt) AS promotion_show_cnt,
        SUM(click_cnt) AS promotion_click_cnt,
        SUM(convert_cnt) AS promotion_convert_cnt,
        SUM(oto_pay_order_count) AS promotion_oto_pay_order_count,
        SUM(oto_pay_order_amount) AS promotion_oto_pay_order_amount,
        SUM(video_oto_pay_order_count) AS promotion_video_oto_pay_order_count,
        SUM(video_oto_pay_order_stat_amount) AS promotion_video_oto_pay_order_amount,
        SUM(live_oto_pay_order_count) AS promotion_live_oto_pay_order_count,
        SUM(live_oto_pay_order_stat_amount) AS promotion_live_oto_pay_order_amount,
        SUM(poi_recommend_count) AS promotion_poi_recommend_count,
        SUM(poi_homepage_view_count) AS promotion_poi_homepage_view_count
    FROM ods_data_local_ads_promotion_detail
    WHERE ds >= '20260501'
      AND stat_time_day = '${bizdate}'
    GROUP BY adv_id, cdp_project_id, cdp_promotion_id
),
poi_ad_metric AS (
    SELECT
        adv_id,
        ad_id,
        MAX(ad_info_name) AS poi_ad_info_name,
        SUM(video_stat_cost_for_roi2) AS poi_ad_cost,
        SUM(video_oto_pay_order_count_for_roi2) AS poi_ad_pay_order_count,
        SUM(video_oto_pay_order_stat_amount_for_roi2) AS poi_ad_pay_order_amount,
        MAX(video_oto_pay_order_roi2_new) AS poi_ad_roi,
        SUM(video_oto_pay_qcpx_coupon_stat_amount_for_roi2) AS poi_ad_coupon_amount,
        SUM(qcpx_coupon_video_oto_pay_order_count_for_roi2) AS poi_ad_coupon_order_count,
        SUM(qcpx_coupon_video_oto_pay_order_stat_amount_for_roi2) AS poi_ad_coupon_order_amount
    FROM ods_data_local_ads_poi_ad_stats
    WHERE ds >= '20260501'
      AND stat_time_day = '${bizdate}'
    GROUP BY adv_id, ad_id
),
script_video AS (
    SELECT
        item_id AS video_id,
        MAX(douyin_url) AS douyin_url,
        MAX(douyin_id) AS douyin_id,
        MAX(author_uid) AS author_uid,
        MAX(nickname) AS script_author_name,
        MAX(fans_num_all) AS script_author_fans_cnt,
        MAX(item_title) AS video_title,
        MAX(item_create_ts) AS video_publish_time,
        SUM(item_pay_gmv) AS item_pay_gmv,
        SUM(item_indirect_pay_gmv) AS item_indirect_pay_gmv,
        SUM(item_pay_gmv_all) AS item_pay_gmv_all,
        SUM(item_play_cnt) AS script_video_play_cnt,
        SUM(item_comment_cnt) AS script_video_comment_cnt,
        SUM(item_like_cnt) AS script_video_like_cnt,
        SUM(item_share_cnt) AS script_video_share_cnt,
        MAX(ai_script_content) AS ai_script_content
    FROM dws_sales_talent_video_script_detail
    WHERE ds >= '20260501'
    GROUP BY item_id
)
SELECT
    t.order_id,
    t.merchant_order_no,
    t.order_tag,
    t.order_status,
    t.after_sale_flag,
    t.place_order_time,
    t.pay_time,
    t.product_name,
    t.product_id,
    t.quantity,
    t.customer_actual_pay AS pay_amount,
    t.order_actual_receipt,
    t.total_refund_amount,
    t.refund_amount,
    t.verification_status,
    t.verification_time,
    t.verify_record_id,
    t.verify_province,
    t.verify_city,
    t.verify_store_id,
    t.verify_store_name,
    t.verify_status,
    t.verify_time,
    t.adv_id,
    t.cdp_promotion_id,
    t.cdp_promotion_name,
    t.cdp_marketing_goal,
    t.oto_pay_order_amount,
    t.ad_id,
    t.ad_info_name,
    CASE
        WHEN t.cdp_promotion_id IS NOT NULL THEN '标准投放'
        WHEN t.ad_id IS NOT NULL THEN '门店全域'
        ELSE '自然/未知'
    END AS ad_scene,
    t.content_url,
    t.talent_nickname,
    t.talent_douyin_id,
    t.talent_uid,
    t.promoter_name,
    t.transaction_channel,
    m.project_id,
    m.project_name,
    m.promotion_name,
    m.material_cnt,
    m.ad_cost,
    m.show_cnt,
    m.click_cnt,
    m.convert_cnt,
    m.video_play_cnt,
    m.video_like_cnt,
    m.video_comment_cnt,
    m.video_share_cnt,
    s.video_id,
    s.video_title,
    s.video_publish_time,
    s.douyin_url,
    s.douyin_id,
    COALESCE(au.author_id, CAST(s.author_uid AS STRING), t.talent_uid) AS author_id,
    COALESCE(au.author_name, s.script_author_name, t.talent_nickname) AS author_name,
    au.author_level,
    COALESCE(au.author_fans_cnt, s.script_author_fans_cnt) AS author_fans_cnt,
    ac.author_credit_score,
    ac.author_new_credit_score,
    ac.author_order_cnt,
    ac.author_process_order_cnt,
    ac.author_max_process_order_cnt,
    la.linke_uid,
    la.linke_city_name,
    la.linke_fans_count,
    la.linke_local_fans_count,
    la.linke_item_gmv,
    la.linke_item_order_cnt,
    la.linke_verify_rate_30d,
    lv.latest_item_id,
    lv.latest_video_title,
    lv.latest_video_date,
    avm.avg_duration_30d,
    avm.comment_avg_30d,
    avm.like_avg_30d,
    avm.share_avg_30d,
    avm.item_num_30d,
    s.item_pay_gmv,
    s.item_indirect_pay_gmv,
    s.item_pay_gmv_all,
    s.ai_script_content,
    pm.promotion_stat_cost,
    pm.promotion_show_cnt,
    pm.promotion_click_cnt,
    pm.promotion_convert_cnt,
    pm.promotion_oto_pay_order_count,
    pm.promotion_oto_pay_order_amount,
    pm.promotion_video_oto_pay_order_count,
    pm.promotion_video_oto_pay_order_amount,
    pm.promotion_live_oto_pay_order_count,
    pm.promotion_live_oto_pay_order_amount,
    pam.poi_ad_cost,
    pam.poi_ad_pay_order_count,
    pam.poi_ad_pay_order_amount,
    pam.poi_ad_roi,
    GETDATE() AS etl_time
FROM trade_base t
LEFT JOIN material_metric m
    ON t.adv_id = m.adv_id
   AND t.cdp_promotion_id = m.promotion_id
LEFT JOIN script_video s
    ON t.content_url = s.douyin_url
LEFT JOIN author_dim au
    ON t.talent_uid = au.author_id
    OR t.talent_douyin_id = au.author_unique_id
LEFT JOIN author_video_metric avm
    ON COALESCE(au.author_id, CAST(s.author_uid AS STRING), t.talent_uid) = avm.author_id
LEFT JOIN author_credit ac
    ON COALESCE(au.author_id, CAST(s.author_uid AS STRING), t.talent_uid) = ac.author_id
LEFT JOIN linke_author la
    ON t.talent_uid = la.linke_uid
    OR t.talent_douyin_id = la.linke_douyin_id
    OR t.talent_douyin_id = la.linke_unique_id
LEFT JOIN latest_video lv
    ON COALESCE(au.author_id, CAST(s.author_uid AS STRING), t.talent_uid) = lv.author_id
LEFT JOIN promotion_metric pm
    ON t.adv_id = pm.adv_id
   AND t.cdp_promotion_id = pm.cdp_promotion_id
LEFT JOIN poi_ad_metric pam
    ON t.adv_id = pam.adv_id
   AND t.ad_id = pam.ad_id
;
```

说明：上面的 SQL 是结构骨架，不是可直接上线版本。订单主表、达人基础、达人传播价值、素材指标、脚本视频表字段名已按 MaxCompute 元数据修正；但达人 ID 体系、`content_url` 与 `douyin_url` 的 URL 格式一致性仍需抽样验证。

## 9. 数据质量校验

### 9.1 分区行数

```sql
SELECT ds, COUNT(*) AS row_cnt
FROM dws_local_life_trade_marketing_wide_di
WHERE ds >= '20260501'
GROUP BY ds;
```

### 9.2 主键重复

```sql
SELECT order_id, verify_record_id, verify_store_id, COUNT(*) AS cnt
FROM dws_local_life_trade_marketing_wide_di
WHERE ds >= '20260501'
GROUP BY order_id, verify_record_id, verify_store_id
HAVING COUNT(*) > 1
LIMIT 100;
```

### 9.3 金额对账

```sql
SELECT
    SUM(pay_amount) AS pay_amount,
    SUM(order_actual_receipt) AS order_actual_receipt,
    SUM(refund_amount) AS refund_amount
FROM dws_local_life_trade_marketing_wide_di
WHERE ds >= '20260501';
```

与主事实表 `dwd_data_life_douyin_trade_verify_order_poi` 同 `ds` 分区金额进行对账，误差应为 0；如果存在一对多投放/素材 Join，则必须先修正去重或聚合逻辑。

### 9.4 核心字段空值率

```sql
SELECT
    COUNT(*) AS row_cnt,
    SUM(CASE WHEN order_id IS NULL OR order_id = '' THEN 1 ELSE 0 END) AS null_order_id_cnt,
    SUM(CASE WHEN verify_store_id IS NULL OR verify_store_id = '' THEN 1 ELSE 0 END) AS null_verify_store_id_cnt,
    SUM(CASE WHEN cdp_promotion_id IS NULL OR cdp_promotion_id = '' THEN 1 ELSE 0 END) AS null_cdp_promotion_id_cnt,
    SUM(CASE WHEN author_id IS NULL OR author_id = '' THEN 1 ELSE 0 END) AS null_author_id_cnt,
    SUM(CASE WHEN video_id IS NULL OR video_id = '' THEN 1 ELSE 0 END) AS null_video_id_cnt
FROM dws_local_life_trade_marketing_wide_di
WHERE ds >= '20260501';
```

## 10. 开发顺序

1. 已读取核心依赖表字段元数据：`dwd_data_life_douyin_trade_verify_order_poi`、`ods_data_xt_author_base_info`、`ods_data_xt_author_video_metrics`、`ods_data_local_ads_material`、`dws_sales_talent_video_script_detail`。
2. 确认主表粒度和订单唯一键，判断 `order_id`、`verify_record_id`、`verify_store_id`、`cdp_promotion_id`、`ad_id`、`content_url`、`talent_uid` 是否可作为 V1/V2 连接字段。
3. 先开发只包含订单、核销、投放、POI 的 V1。
4. 再接入达人、视频、素材字段作为 V2。
5. 最后考虑直播归因和内容脚本字段作为 V3。

## 11. 当前风险与待确认项

| 风险 | 说明 | 处理方式 |
|---|---|---|
| 字段名部分已知 | 第一批 5 张 + 第二批 10 张表字段已读取；第三批 10 张达人/POI/门店/品牌候选表已读取 | 后续只需按落地范围补充更细维表 |
| Join Key 不确定 | 投放、素材、视频、达人、直播间 ID 体系可能不统一 | 先用字段探查确认同名字段和样例值 |
| 一对多放大金额 | 订单关联多个素材/视频可能导致金额重复 | 投放/素材侧先聚合到订单粒度或保留 attribution_rank |
| ODS 与 DWD 重复来源 | 同一业务存在 `ods_data_*` 和 `ods_xd_manage_*` 两套表 | 优先 DWD，其次选择更新时间稳定的一套 ODS |
| 19 张新增未映射表 | 部分 ADS/DWD/AI 测试表未进入 `-1.md` 权限映射 | 先不作为强依赖，确认后补权限和业务线 |

## 12. 下一步元数据探查清单

已完成优先级最高的 5 张表元数据探查：

1. `dwd_data_life_douyin_trade_verify_order_poi`
2. `ods_data_xt_author_base_info`
3. `ods_data_xt_author_video_metrics`
4. `ods_data_local_ads_material`
5. `dws_sales_talent_video_script_detail`

已完成第二批 10 张表元数据探查：

1. `dwd_union_ads_order_poi_order_detail`
2. `ods_data_life_douyin_trade_detail`
3. `ods_data_life_douyin_verify_detail`
4. `ods_data_local_ads_order_detail`
5. `ods_data_local_ads_poi_order_detail`
6. `ods_data_local_ads_project_stats`
7. `ods_data_local_ads_promotion_detail`
8. `ods_data_xt_author_credit_data`
9. `ods_xd_manage_data_local_ads_live_material_detail`
10. `ods_data_syj_live`

已完成第三批 10 张表元数据探查：

1. `ods_data_linke_author_wide`
2. `ods_data_xt_author_latest_video`
3. `ods_data_local_ads_poi_ad_stats`
4. `ods_conf_brand_store_address`
5. `ods_conf_store`
6. `ods_conf_store_0411`
7. `ods_data_douyin_dealer_manage_list`
8. `ods_dealer_store`
9. `ods_dealer_store_account`
10. `ods_brand_detail`

建议下一步从“继续读表”转为“抽样验证 Join Key”：

1. 抽样验证 `talent_uid`、`talent_douyin_id` 与林客/星图达人表 ID 的匹配率。
2. 抽样验证 `content_url` 与 `douyin_url` 的格式一致性。
3. 抽样验证 `verify_store_id`、`verify_store_name` 与内部门店/经销商门店维表是否存在可用映射。
4. 校验接入 `promotion_metric`、`poi_ad_metric` 后订单金额是否被一对多放大。
