# 数仓表资产第一轮分类盘点

## 结论摘要

- 本地表清单总数：691 张
- 已匹配业务线映射：672 张
- 未匹配业务线映射：19 张
- 缺少中文说明/注释：266 张

## 按数仓分层统计

| 分层 | 表数 |
|---|---:|
| ods | 677 |
| ads | 6 |
| dwd | 6 |
| dws | 1 |
| tmp | 1 |

## 按业务线统计

| 业务线 | 表数 |
|---|---:|
| 职能后台 | 225 |
| 内容创意 | 111 |
| 投流/投放 | 105 |
| 达人 | 76 |
| 直播 | 76 |
| 销售/商业化 | 35 |
| 技术研发 | 23 |
| 未映射 | 19 |
| 本地通 | 12 |
| 本地生活 | 9 |

## 按主题域统计

| 主题域 | 表数 | 样例 |
|---|---:|---|
| 视频/内容/素材 | 118 | `ads_sales_talent_video_hot_script`, `ads_sales_talent_video_script`, `ads_sales_talent_video_script_top30_metrics`, `ads_talent_video_project_summary_metrics`, `ads_talent_video_top10_ranking`, `dwd_sales_influencer_video_comment_influencer`, `dwd_sales_sales_influencer_coop_project_influencer_video`, `dwd_syj_video_coop_project_library` |
| 线索/私信/客户 | 85 | `ods_c_client`, `ods_c_client_live`, `ods_c_client_message`, `ods_c_client_report`, `ods_c_client_video`, `ods_c_customer_message_reply`, `ods_c_live_client_accurate_option`, `ods_c_video_strategy` |
| 组织/用户/权限 | 81 | `ods_account_allocation_record`, `ods_agent_account_group`, `ods_agent_account_group_item`, `ods_business_user`, `ods_conf_flow_group`, `ods_conf_organization`, `ods_conf_sys_news`, `ods_conf_user_guide` |
| 直播 | 78 | `ods_ai_live_config`, `ods_ai_live_reply`, `ods_business_live_detail`, `ods_business_live_list`, `ods_business_live_list_qianchuan`, `ods_business_live_list_v2`, `ods_business_live_review_v2`, `ods_c_live_keyword` |
| 未分类 | 63 | `ods_checkpoints`, `ods_city`, `ods_conf_city`, `ods_conf_db_version`, `ods_conf_industry`, `ods_conf_lock`, `ods_conf_region`, `ods_conf_watch_level` |
| 日志/任务/系统 | 61 | `ods_ai_live_reply_history`, `ods_ai_reply_history`, `ods_ai_test_fxp_video_auto_task`, `ods_ai_test_video_analysis_task`, `ods_ai_video_reply_history`, `ods_bdt_user_operation_log`, `ods_brand_log`, `ods_checkpoint_blobs` |
| 达人/作者 | 50 | `ods_ai_test_gm_douyin_bloger`, `ods_conf_douyin_hot_creator_data`, `ods_data_douyin_lin_ke`, `ods_data_linke_author_credit_info`, `ods_data_linke_author_page`, `ods_data_linke_author_sales_data`, `ods_data_linke_author_wide`, `ods_data_xt_author_base_info` |
| AI/知识库/机器人 | 44 | `ods_ai_prompt_config`, `ods_ai_reply`, `ods_ai_reply_template`, `ods_ai_test_create_file_id_record`, `ods_ai_test_create_file_id_record_split`, `ods_ai_test_gm_douyin_videos`, `ods_ai_test_knowledgebase_docs`, `ods_ai_test_knowledgebase_points` |
| 广告/投放 | 39 | `ads_sales_bi`, `ods_agent_ocean_user_bind`, `ods_agent_ocean_user_bind_advertiser`, `ods_agent_ocean_user_bind_group`, `ods_ai_test_ocean_local_project_big`, `ods_data_business_ocean_bidding`, `ods_data_business_promotion_daily`, `ods_data_douyin_employee_account_detail` |
| 汽车/品牌/车型 | 25 | `ods_backup_table_car_model_info2`, `ods_brand_community`, `ods_brand_detail`, `ods_brand_region`, `ods_brand_region_community_relation`, `ods_brand_region_relation`, `ods_car_info`, `ods_car_model_info` |
| 订单交易 | 21 | `dwd_data_life_douyin_trade_verify_order_poi`, `dwd_union_ads_order_poi_order_detail`, `dwd_xd_manage_data_life_douyin_sales_detail_99`, `ods_data_life_douyin_trade_detail`, `ods_data_life_douyin_verify_detail`, `ods_data_local_ads_order_detail`, `ods_data_local_ads_poi_order_detail`, `ods_data_xt_author_credit_data` |
| 门店/经销商/POI | 20 | `ods_conf_brand_store_address`, `ods_conf_store`, `ods_conf_store_0411`, `ods_data_autoengine_cnr_cost`, `ods_data_douyin_dealer_manage_list`, `ods_dealer_store`, `ods_dealer_store_account`, `ods_dealer_store_operation_record` |
| 财务/成本/结算 | 6 | `ods_t_monitor_budget_cost_alter`, `ods_t_monitor_invalid_cost_alter`, `ods_t_org_cost_conf`, `ods_xd_manage_t_monitor_budget_cost_alter`, `ods_xd_manage_t_monitor_invalid_cost_alter`, `ods_xd_manage_t_org_cost_conf` |

## 优先处理建议

1. 先处理 `订单交易`、`线索/私信/客户`、`直播`、`视频/内容/素材`、`广告/投放` 五类，它们更接近常用业务分析和报表需求。
2. 对每个主题域分批读取字段元数据，每批控制在 20-40 张表，避免一次性扫描 MaxCompute 元数据时间过长。
3. 对 `未分类`、`未映射`、缺少注释的表单独做二次识别，优先补表说明和负责人/业务线。
4. 月份后缀、历史表、临时表先归并为同一逻辑表族，避免资产口径被重复表膨胀。

## 未匹配业务线样例

- `ads_sales_bi`
- `ads_sales_talent_video_script_top30_metrics`
- `ads_talent_video_project_summary_metrics`
- `ads_talent_video_top10_ranking`
- `dwd_sales_influencer_video_comment_influencer`
- `dwd_sales_sales_influencer_coop_project_influencer_video`
- `dwd_syj_video_coop_project_library`
- `ods_ai_test_create_file_id_record`
- `ods_ai_test_create_file_id_record_split`
- `ods_ai_test_fxp_video_auto_task`
- `ods_ai_test_gm_douyin_bloger`
- `ods_ai_test_gm_douyin_videos`
- `ods_ai_test_knowledgebase_docs`
- `ods_ai_test_knowledgebase_points`
- `ods_ai_test_localad_pois`
- `ods_ai_test_ocean_local_project_big`
- `ods_ai_test_project_analyse_result`
- `ods_ai_test_prompt_config`
- `ods_ai_test_video_analysis_task`
