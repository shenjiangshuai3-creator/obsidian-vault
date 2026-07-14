-- XHS mock warehouse schema for MaxCompute.
-- This schema is for personal learning and synthetic data only.

CREATE TABLE IF NOT EXISTS xhs_note (
    note_id STRING COMMENT '笔记ID',
    account_id STRING COMMENT '账号ID',
    note_title STRING COMMENT '标题',
    content_type STRING COMMENT 'image_text, short_video, live_replay',
    publish_time DATETIME COMMENT '发布时间',
    keyword_main STRING COMMENT '主关键词',
    topic STRING COMMENT '话题',
    product_id STRING COMMENT '商品ID',
    kol_id STRING COMMENT '达人ID',
    source_type STRING COMMENT 'organic, kol_coop, ad',
    note_url STRING COMMENT '笔记链接',
    created_at DATETIME COMMENT '创建时间'
) COMMENT '小红书笔记基础信息';

CREATE TABLE IF NOT EXISTS xhs_note_daily_metrics (
    metric_date STRING COMMENT '指标日期',
    note_id STRING COMMENT '笔记ID',
    impressions BIGINT COMMENT '曝光',
    clicks BIGINT COMMENT '点击',
    likes BIGINT COMMENT '点赞',
    collects BIGINT COMMENT '收藏',
    comments BIGINT COMMENT '评论',
    shares BIGINT COMMENT '分享',
    follows BIGINT COMMENT '关注',
    orders BIGINT COMMENT '订单数',
    gmv DECIMAL(18, 2) COMMENT 'GMV'
) COMMENT '小红书笔记每日指标';

CREATE TABLE IF NOT EXISTS xhs_account_daily_metrics (
    metric_date STRING COMMENT '指标日期',
    account_id STRING COMMENT '账号ID',
    followers BIGINT COMMENT '粉丝数',
    new_followers BIGINT COMMENT '新增粉丝',
    profile_views BIGINT COMMENT '主页访问',
    total_impressions BIGINT COMMENT '总曝光',
    total_interactions BIGINT COMMENT '总互动'
) COMMENT '小红书账号每日指标';

CREATE TABLE IF NOT EXISTS xhs_keyword_trend (
    metric_date STRING COMMENT '指标日期',
    keyword_name STRING COMMENT '关键词',
    search_index BIGINT COMMENT '搜索指数',
    note_count BIGINT COMMENT '笔记数',
    avg_interaction_rate DECIMAL(10, 6) COMMENT '平均互动率'
) COMMENT '小红书关键词趋势';

CREATE TABLE IF NOT EXISTS xhs_kol_profile (
    kol_id STRING COMMENT '达人ID',
    kol_name STRING COMMENT '达人名称',
    category STRING COMMENT '领域',
    follower_count BIGINT COMMENT '粉丝数',
    avg_like_count BIGINT COMMENT '平均点赞',
    avg_collect_count BIGINT COMMENT '平均收藏',
    quote_price DECIMAL(18, 2) COMMENT '报价'
) COMMENT '小红书达人画像';

CREATE TABLE IF NOT EXISTS xhs_kol_cooperation (
    coop_id STRING COMMENT '合作ID',
    kol_id STRING COMMENT '达人ID',
    note_id STRING COMMENT '笔记ID',
    coop_date STRING COMMENT '合作日期',
    coop_cost DECIMAL(18, 2) COMMENT '合作成本',
    expected_gmv DECIMAL(18, 2) COMMENT '预期GMV',
    actual_gmv DECIMAL(18, 2) COMMENT '实际GMV',
    status STRING COMMENT '状态'
) COMMENT '小红书达人合作记录';

CREATE TABLE IF NOT EXISTS xhs_campaign_daily_metrics (
    metric_date STRING COMMENT '指标日期',
    campaign_id STRING COMMENT '计划ID',
    campaign_name STRING COMMENT '计划名称',
    spend DECIMAL(18, 2) COMMENT '花费',
    impressions BIGINT COMMENT '曝光',
    clicks BIGINT COMMENT '点击',
    conversions BIGINT COMMENT '转化',
    gmv DECIMAL(18, 2) COMMENT 'GMV'
) COMMENT '小红书广告投放日报';

CREATE TABLE IF NOT EXISTS xhs_product (
    product_id STRING COMMENT '商品ID',
    product_name STRING COMMENT '商品名称',
    category STRING COMMENT '类目',
    price DECIMAL(18, 2) COMMENT '价格',
    status STRING COMMENT '状态'
) COMMENT '小红书商品基础信息';

CREATE TABLE IF NOT EXISTS xhs_order (
    order_id STRING COMMENT '订单ID',
    order_time DATETIME COMMENT '订单时间',
    product_id STRING COMMENT '商品ID',
    note_id STRING COMMENT '笔记ID',
    account_id STRING COMMENT '账号ID',
    source_type STRING COMMENT '来源类型',
    quantity BIGINT COMMENT '数量',
    order_amount DECIMAL(18, 2) COMMENT '订单金额',
    order_status STRING COMMENT '订单状态'
) COMMENT '小红书订单数据';

