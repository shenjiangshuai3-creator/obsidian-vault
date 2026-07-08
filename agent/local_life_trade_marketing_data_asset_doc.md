# 本地生活交易营销数据资产文档

> 资产对象：`dws_local_life_trade_marketing_wide_di` 及其核心依赖表  
> 适用范围：本地生活订单交易、核销、投放转化、达人内容、门店/POI、直播扩展分析  
> 版本日期：2026-07-08

---

## 1. 资产概览

### 1.1 资产定位

`dws_local_life_trade_marketing_wide_di` 是面向本地生活经营分析的 DWS 明细宽表，目标是打通订单、核销、标准投放、门店全域投放、达人、视频内容、素材、门店/品牌等数据链路，为成交、核销、退款、投放 ROI、达人内容贡献和门店经营效果提供统一分析底座。

### 1.2 建设目标

- 统一本地生活交易、核销、投放、内容、达人和门店分析口径。
- 减少业务分析中反复 Join ODS/DWD 明细表的成本。
- 为 BI 看板、专题分析、投放复盘、达人内容评估提供可复用资产。
- 保留订单/核销明细粒度，支持后续派生门店日、达人日、投放单元日等汇总资产。

### 1.3 推荐粒度

第一版推荐采用“订单/核销明细粒度”。

优先唯一键：

1. `order_id + verify_record_id + verify_store_id + ds`
2. 若无核销记录：`order_id + verify_store_id + ds`
3. 若投放或素材侧存在一对多关系，需先聚合到订单或单元日粒度，避免金额重复。

### 1.4 分区与更新方式

| 项目 | 说明 |
|---|---|
| 分区字段 | `ds` |
| 分区格式 | `yyyyMMdd` |
| 当前查询口径 | `ds >= '20260501'` |
| 推荐写入方式 | 按日分区覆盖写入 |
| 数据保留 | 保留订单最新状态及核销明细 |

---

## 2. 业务价值与使用场景

| 场景 | 典型问题 | 主要字段/指标 |
|---|---|---|
| 交易分析 | 本地生活订单成交、支付、退款、核销情况如何？ | `order_id`, `pay_amount`, `verify_amount`, `refund_amount`, `verify_status` |
| 投放转化 | 标准投放和门店全域分别带来多少成交？ROI 如何？ | `adv_id`, `cdp_promotion_id`, `ad_id`, `ad_cost`, `poi_ad_roi` |
| 达人分析 | 哪些达人、内容、视频贡献了成交？ | `talent_uid`, `author_id`, `author_name`, `video_id`, `item_pay_gmv` |
| 素材分析 | 哪些素材带来曝光、点击、转化和成交？ | `material_cnt`, `show_cnt`, `click_cnt`, `convert_cnt` |
| 门店经营 | 哪些门店、城市、品牌核销和成交表现更好？ | `verify_store_id`, `verify_store_name`, `verify_city`, `brand_name` |
| 直播扩展 | 直播间经营与本地生活成交是否有关联？ | `room_id`, `live_gmv`, `live_verify_amount` |

---

## 3. 数据资产目录

### 3.1 目标资产

| 表名 | 分层 | 主题域 | 资产角色 | 说明 |
|---|---|---|---|---|
| `dws_local_life_trade_marketing_wide_di` | DWS | 本地生活交易营销 | 目标宽表 | 融合订单、核销、投放、达人、内容、门店等跨主题域数据 |

### 3.2 核心事实资产

| 表名 | 分层 | 主题域 | 角色 | 说明 |
|---|---|---|---|---|
| `dwd_data_life_douyin_trade_verify_order_poi` | DWD | 订单交易 | 主事实表 | 订单、核销、标准投放、门店全域一体化主事实宽表 |
| `ods_data_life_douyin_trade_detail` | ODS | 订单交易 | 订单明细来源 | 抖音来客成交订单明细 |
| `ods_data_life_douyin_verify_detail` | ODS | 订单交易 | 核销明细来源 | 抖音来客核销明细 |
| `ods_data_local_ads_order_detail` | ODS | 广告/投放 | 标准投放成单 | 本地推标准投放单元级成单明细 |
| `ods_data_local_ads_poi_order_detail` | ODS | 广告/投放 | 门店全域成单 | 本地推门店全域单元级成单明细 |
| `dwd_union_ads_order_poi_order_detail` | DWD | 订单交易 | 校验集合 | 投放和门店全域成单 `order_id` 集合，仅适合作圈选/校验 |

### 3.3 投放与素材资产

| 表名 | 分层 | 主题域 | 角色 | 说明 |
|---|---|---|---|---|
| `ods_data_local_ads_project_stats` | ODS | 广告/投放 | 项目级投放指标 | 标准投放项目级日指标 |
| `ods_data_local_ads_promotion_detail` | ODS | 广告/投放 | 单元级投放指标 | 标准投放单元级消耗、曝光、点击、成交等指标 |
| `ods_data_local_ads_material` | ODS | 视频/内容/素材 | 素材级指标 | 标准投放素材级消耗、互动、成交指标 |
| `ods_data_local_ads_poi_ad_stats` | ODS | 广告/投放 | 门店全域指标 | 门店全域单元级消耗、成交金额、订单数、ROI 指标 |

### 3.4 达人与内容资产

| 表名 | 分层 | 主题域 | 角色 | 说明 |
|---|---|---|---|---|
| `ods_data_xt_author_base_info` | ODS | 达人/作者 | 达人基础维表 | 巨量星图达人基础信息，真实名称字段为 `nick_name`，粉丝字段为 `follower` |
| `ods_data_xt_author_credit_data` | ODS | 达人/作者 | 达人履约能力 | 达人信用分、订单能力、履约能力指标 |
| `ods_data_xt_author_video_metrics` | ODS | 达人/作者 | 达人传播指标 | 达人级近 30/90 天传播能力指标，不是单视频明细 |
| `ods_data_xt_author_latest_video` | ODS | 视频/内容/素材 | 最新视频维度 | 作者最新视频信息，用于补充最近内容维度 |
| `ods_data_linke_author_wide` | ODS | 达人/作者 | 林客达人宽表 | 抖音林客达人 UID、抖音号、粉丝、本地粉丝、视频 GMV 等宽表 |
| `dws_sales_talent_video_script_detail` | DWS | 视频/内容/素材 | 视频脚本明细 | 单条视频指标与 AI 脚本明细，包含 `item_id`、`douyin_url`、`author_uid`、`ai_script_content` |

### 3.5 门店、品牌与直播扩展资产

| 表名 | 分层 | 主题域 | 角色 | 说明 |
|---|---|---|---|---|
| `ods_conf_store` | ODS | 门店/经销商/POI | 内部门店配置 | 内部门店、组织、巨量组织、直播房间、省市、品牌名配置 |
| `ods_conf_brand_store_address` | ODS | 门店/经销商/POI | 品牌门店地址 | 品牌全国门店地址，缺少稳定抖音 POI ID |
| `ods_dealer_store` | ODS | 门店/经销商/POI | 经销商门店维表 | 门店 ID、品牌 ID、城市、门店等级和状态 |
| `ods_dealer_store_account` | ODS | 门店/经销商/POI | 门店账户 | 经销商门店账户，可通过 `store_id` 关联门店 |
| `ods_brand_detail` | ODS | 汽车/品牌/车型 | 品牌维表 | 品牌 ID、品牌名称、品牌状态 |
| `ods_xd_manage_data_local_ads_live_material_detail` | ODS | 直播 | 直播投放素材 | 直播全域投放素材明细，含直播消耗、成交、观看、互动指标 |
| `ods_data_syj_live` | ODS | 直播 | 直播经营指标 | 生意经直播间 GMV、核销、退款、曝光、观看、门店账号等指标 |

---

## 4. 主题域模型

| 主题域 | 资产能力 | 核心表 |
|---|---|---|
| 订单交易 | 提供订单、支付、退款、核销、商品、门店核销链路 | `dwd_data_life_douyin_trade_verify_order_poi`, `ods_data_life_douyin_trade_detail`, `ods_data_life_douyin_verify_detail` |
| 广告/投放 | 提供标准投放、门店全域、项目、单元、消耗、转化、ROI | `ods_data_local_ads_promotion_detail`, `ods_data_local_ads_project_stats`, `ods_data_local_ads_poi_ad_stats` |
| 达人/作者 | 提供达人基础资料、粉丝、信用、履约、传播能力 | `ods_data_xt_author_base_info`, `ods_data_xt_author_credit_data`, `ods_data_linke_author_wide` |
| 视频/内容/素材 | 提供素材、视频、脚本、播放、互动、内容成交贡献 | `ods_data_local_ads_material`, `dws_sales_talent_video_script_detail`, `ods_data_xt_author_latest_video` |
| 门店/品牌 | 提供核销门店、经销商门店、城市、品牌、账户属性 | `ods_conf_store`, `ods_dealer_store`, `ods_brand_detail` |
| 直播 | 提供直播间经营、直播投放素材与直播成交扩展能力 | `ods_xd_manage_data_local_ads_live_material_detail`, `ods_data_syj_live` |

---

## 5. 核心口径定义

### 5.1 交易口径

| 口径 | 定义 | 推荐来源 |
|---|---|---|
| 订单数 | 明细粒度下通常每行计 1，汇总时按唯一键去重 | `order_id` |
| 支付金额 | 用户实际支付金额 | `customer_actual_pay` 映射为 `pay_amount` |
| 订单实收 | 商家/平台订单实收金额 | `order_actual_receipt` |
| 退款金额 | 订单退款金额 | `refund_amount`, `total_refund_amount` |
| 核销金额 | 券或订单核销金额 | `hx_card_verify_amount`、DWD 核销相关字段 |
| 核销状态 | 订单或券核销状态 | `verify_status`, `verification_status` |

### 5.2 投放口径

| 口径 | 定义 | 推荐来源 |
|---|---|---|
| 标准投放 | DWD 中命中 `cdp_promotion_id` 的订单链路 | `ods_data_local_ads_order_detail`, `ods_data_local_ads_promotion_detail` |
| 门店全域 | DWD 中命中 `ad_id` 的门店全域订单链路 | `ods_data_local_ads_poi_order_detail`, `ods_data_local_ads_poi_ad_stats` |
| 广告消耗 | 投放项目/单元/素材统计的消耗金额 | `stat_cost`, `video_stat_cost_for_roi2` |
| 曝光点击转化 | 投放或素材统计的曝光、点击、转化指标 | `show_cnt`, `click_cnt`, `convert_cnt` |
| ROI | 支付成交金额 / 投放消耗 | `video_oto_pay_order_roi2_new` 或计算口径 |

### 5.3 达人与内容口径

| 口径 | 定义 | 推荐来源 |
|---|---|---|
| 达人 ID | 统一后的达人主键，优先验证 `talent_uid`、`author_id`、`uid` 的关系 | DWD、星图、林客达人表 |
| 达人名称 | 达人昵称或作者名称 | `nick_name`, `nickname`, `talent_nickname` |
| 粉丝数 | 达人粉丝规模 | `follower`, `fans_count`, `fans_num_all` |
| 视频 ID | 单条内容标识 | `item_id`, `video_id` |
| 视频 GMV | 视频直接/间接成交 GMV | `item_pay_gmv`, `item_indirect_pay_gmv`, `item_pay_gmv_all` |
| AI 脚本 | 视频对应的脚本内容 | `ai_script_content` |

### 5.4 门店口径

| 口径 | 定义 | 推荐来源 |
|---|---|---|
| 核销门店 | 订单或券实际核销的门店 | `verify_store_id`, `verify_store_name` |
| 内部门店 | 企业内部维护的门店主体 | `ods_conf_store` |
| 经销商门店 | 经销商体系下的门店 | `ods_dealer_store` |
| 品牌 | 门店关联品牌 | `ods_brand_detail.brand_name` |
| 城市 | 核销或门店所在城市 | `verify_city`, `city_name` |

---

## 6. 数据血缘

### 6.1 主事实链路

```text
ods_data_life_douyin_trade_detail
  LEFT JOIN ods_data_life_douyin_verify_detail       ON order_id
  LEFT JOIN ods_data_local_ads_order_detail          ON order_id
  LEFT JOIN ods_data_local_ads_poi_order_detail      ON order_id
        ↓
dwd_data_life_douyin_trade_verify_order_poi
        ↓
dws_local_life_trade_marketing_wide_di
```

### 6.2 扩展维度与指标链路

```text
dwd_data_life_douyin_trade_verify_order_poi
  ├─ 标准投放指标：ods_data_local_ads_promotion_detail / ods_data_local_ads_material
  ├─ 门店全域指标：ods_data_local_ads_poi_ad_stats
  ├─ 达人基础属性：ods_data_xt_author_base_info / ods_data_linke_author_wide
  ├─ 达人履约指标：ods_data_xt_author_credit_data
  ├─ 视频脚本指标：dws_sales_talent_video_script_detail
  ├─ 门店品牌属性：ods_conf_store / ods_dealer_store / ods_brand_detail
  └─ 直播扩展指标：ods_xd_manage_data_local_ads_live_material_detail / ods_data_syj_live
```

---

## 7. 关键关联关系

| 关联对象 | Join Key | 可信度 | 说明 |
|---|---|---|---|
| 订单明细 → 核销明细 | `order_id` | 已知 DML 确认 | 一单可能多券或多核销记录 |
| 订单明细 → 标准投放成单 | `order_id` | 已知 DML 确认 | DWD 已接入该链路 |
| 订单明细 → 门店全域成单 | `order_id` | 已知 DML 确认 | DWD 已接入该链路 |
| DWD → 标准投放单元指标 | `adv_id + cdp_promotion_id + stat_time_day` | 强相关 | 指标为单元日粒度，不能直接按订单金额对账 |
| DWD → 素材指标 | `adv_id + cdp_promotion_id/promotion_id + stat_time_day` | 强相关 | 素材侧需先聚合，避免一对多放大 |
| DWD → 门店全域指标 | `adv_id + ad_id + stat_time_day` | 强相关 | 门店全域投放核心键 |
| DWD → 星图达人 | `talent_uid = author_id` 或 `talent_douyin_id = unique_id` | 待验证 | ID 体系可能不一致 |
| DWD → 林客达人 | `talent_uid = uid` 或 `talent_douyin_id = douyin_id/unique_id` | 待验证 | 需抽样验证匹配率 |
| DWD → 视频脚本 | `content_url = douyin_url` | 待验证 | URL 可能存在短链、参数、协议差异 |
| DWD → 门店维表 | `verify_store_id` 或 `verify_store_name` | 待验证 | 名称 Join 仅建议兜底探索 |
| 经销商门店 → 品牌 | `brand_id` | 强相关 | 内部维表链路稳定 |

---

## 8. 推荐字段分组

### 8.1 技术字段

| 字段 | 说明 |
|---|---|
| `ds` | 分区日期 |
| `etl_time` | 写入时间 |
| `source_table_flags` | 命中的来源表标记，便于追溯 |

### 8.2 订单与核销字段

| 字段 | 说明 |
|---|---|
| `order_id` | 订单 ID |
| `verify_record_id` | 核销记录 ID |
| `order_status` | 订单状态 |
| `verify_status` | 核销状态 |
| `refund_status` | 退款状态 |
| `place_order_time` | 下单时间 |
| `pay_time` | 支付时间 |
| `verify_time` | 核销时间 |
| `product_id` / `product_name` | 商品 ID / 商品名称 |
| `pay_amount` | 用户实付金额 |
| `refund_amount` | 退款金额 |

### 8.3 投放字段

| 字段 | 说明 |
|---|---|
| `adv_id` | 广告主 ID |
| `cdp_promotion_id` | 标准投放单元 ID |
| `cdp_promotion_name` | 标准投放单元名称 |
| `ad_id` | 门店全域广告/单元 ID |
| `ad_info_name` | 门店全域广告/单元名称 |
| `ad_scene` | 投放场景：标准投放、门店全域、自然/未知 |
| `ad_cost` | 广告消耗 |
| `show_cnt` | 曝光次数 |
| `click_cnt` | 点击次数 |
| `convert_cnt` | 转化次数 |
| `poi_ad_roi` | 门店全域 ROI |

### 8.4 达人与内容字段

| 字段 | 说明 |
|---|---|
| `talent_uid` | DWD 主表达人 UID |
| `talent_douyin_id` | 达人抖音号/展示 ID |
| `author_id` | 统一后的达人 ID |
| `author_name` | 达人名称 |
| `author_fans_cnt` | 达人粉丝数 |
| `author_credit_score` | 达人信用分 |
| `video_id` | 视频 ID |
| `video_title` | 视频标题 |
| `video_publish_time` | 发布时间 |
| `douyin_url` | 抖音视频 URL |
| `ai_script_content` | AI 脚本内容 |

### 8.5 门店与品牌字段

| 字段 | 说明 |
|---|---|
| `verify_store_id` | 核销门店 ID |
| `verify_store_name` | 核销门店名称 |
| `verify_city` | 核销城市 |
| `store_id` | 内部门店 ID |
| `store_name` | 内部门店名称 |
| `brand_id` | 品牌 ID |
| `brand_name` | 品牌名称 |
| `city_name` | 城市名称 |

---

## 9. 数据质量规则

| 规则 | 校验内容 | 处理建议 |
|---|---|---|
| 分区完整性 | 每个 `ds` 分区是否有数据 | 与 DWD 主事实行数趋势对比 |
| 主键唯一性 | `order_id + verify_record_id + verify_store_id + ds` 是否重复 | 若重复，检查投放/素材/视频一对多 Join |
| 金额对账 | 宽表支付、退款、核销金额与 DWD 主表一致 | 投放指标需单独看，不应与订单金额直接相加 |
| 核心字段空值率 | `order_id`、`verify_store_id`、`adv_id`、`author_id`、`video_id` 空值率 | 按场景分层看，不要求所有行均有达人/视频 |
| Join 命中率 | 达人、视频、门店维表关联命中率 | 低命中需抽样检查 ID 体系或 URL 格式 |
| 指标放大检查 | 接入投放/素材/视频后行数是否增加 | 维度侧先聚合或加 `row_number` 取唯一记录 |

---

## 10. 已知风险与治理建议

| 风险 | 影响 | 建议 |
|---|---|---|
| 达人 ID 体系不统一 | 达人属性和订单无法稳定关联 | 抽样验证 `talent_uid`、`talent_douyin_id`、`author_id`、`uid` 匹配率 |
| 视频 URL 格式不一致 | 内容脚本命中率偏低 | 对 `content_url`、`douyin_url` 做协议、参数、尾斜杠标准化 |
| 素材/视频一对多 | 订单金额被放大 | 素材侧聚合到单元日，视频侧优先 URL 精确匹配 |
| 门店 ID 不同体系 | 门店品牌维度补充失败 | 优先 ID，名称匹配仅做兜底，并输出匹配置信度 |
| 指标粒度混用 | 明细金额和日汇总指标误用 | 字段命名区分订单明细指标与投放日汇总指标 |
| 未映射资产存在 | 权限、负责人、业务线不完整 | 对 19 张未映射表补充业务线、主题域和资产说明 |

---

## 11. 资产运营建议

### 11.1 资产分级

| 等级 | 表范围 | 管理要求 |
|---|---|---|
| P0 核心资产 | `dwd_data_life_douyin_trade_verify_order_poi`, `dws_local_life_trade_marketing_wide_di` | 每日监控、金额对账、主键唯一性校验 |
| P1 重要资产 | 投放、达人、视频、门店核心依赖表 | Join 命中率、分区及时性、字段变更监控 |
| P2 扩展资产 | 直播、品牌地址、经销商账户等扩展表 | 按专题使用时补充校验 |

### 11.2 推荐产出

| 产出 | 用途 |
|---|---|
| 明细宽表 | 支撑灵活分析和问题排查 |
| 门店日汇总表 | 支撑门店经营看板 |
| 投放单元日汇总表 | 支撑投放复盘和 ROI 看板 |
| 达人内容日汇总表 | 支撑达人、视频、脚本贡献分析 |
| 数据质量日报 | 监控分区、行数、主键、金额、命中率 |

---

## 12. 后续待办

1. 抽样验证 `talent_uid`、`talent_douyin_id` 与星图/林客达人表 ID 匹配率。
2. 抽样验证 `content_url` 与 `douyin_url` 的格式一致性。
3. 抽样验证 `verify_store_id`、`verify_store_name` 与内部门店/经销商门店维表匹配率。
4. 校验投放、素材、门店全域指标接入后是否放大订单行数和金额。
5. 将 19 张未映射表补充业务线、负责人、主题域和中文说明。
6. 基于明细宽表派生门店、投放、达人、视频等汇总数据集。
