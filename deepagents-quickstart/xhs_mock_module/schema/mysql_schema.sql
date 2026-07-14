-- XHS mock warehouse schema for MySQL.
-- This schema is for personal learning and synthetic data only.

CREATE TABLE IF NOT EXISTS xhs_note (
    note_id VARCHAR(64) PRIMARY KEY,
    account_id VARCHAR(64) NOT NULL,
    note_title VARCHAR(255) NOT NULL,
    content_type VARCHAR(32) NOT NULL COMMENT 'image_text, short_video, live_replay',
    publish_time DATETIME NOT NULL,
    keyword_main VARCHAR(64),
    topic VARCHAR(64),
    product_id VARCHAR(64),
    kol_id VARCHAR(64),
    source_type VARCHAR(32) NOT NULL COMMENT 'organic, kol_coop, ad',
    note_url VARCHAR(500),
    created_at DATETIME NOT NULL
) COMMENT='小红书笔记基础信息';

CREATE TABLE IF NOT EXISTS xhs_note_daily_metrics (
    metric_date DATE NOT NULL,
    note_id VARCHAR(64) NOT NULL,
    impressions BIGINT NOT NULL,
    clicks BIGINT NOT NULL,
    likes BIGINT NOT NULL,
    collects BIGINT NOT NULL,
    comments BIGINT NOT NULL,
    shares BIGINT NOT NULL,
    follows BIGINT NOT NULL,
    orders BIGINT NOT NULL,
    gmv DECIMAL(18, 2) NOT NULL,
    PRIMARY KEY (metric_date, note_id)
) COMMENT='小红书笔记每日指标';

CREATE TABLE IF NOT EXISTS xhs_account_daily_metrics (
    metric_date DATE NOT NULL,
    account_id VARCHAR(64) NOT NULL,
    followers BIGINT NOT NULL,
    new_followers BIGINT NOT NULL,
    profile_views BIGINT NOT NULL,
    total_impressions BIGINT NOT NULL,
    total_interactions BIGINT NOT NULL,
    PRIMARY KEY (metric_date, account_id)
) COMMENT='小红书账号每日指标';

CREATE TABLE IF NOT EXISTS xhs_keyword_trend (
    metric_date DATE NOT NULL,
    keyword_name VARCHAR(64) NOT NULL,
    search_index BIGINT NOT NULL,
    note_count BIGINT NOT NULL,
    avg_interaction_rate DECIMAL(10, 6) NOT NULL,
    PRIMARY KEY (metric_date, keyword_name)
) COMMENT='小红书关键词趋势';

CREATE TABLE IF NOT EXISTS xhs_kol_profile (
    kol_id VARCHAR(64) PRIMARY KEY,
    kol_name VARCHAR(128) NOT NULL,
    category VARCHAR(64) NOT NULL,
    follower_count BIGINT NOT NULL,
    avg_like_count BIGINT NOT NULL,
    avg_collect_count BIGINT NOT NULL,
    quote_price DECIMAL(18, 2) NOT NULL
) COMMENT='小红书达人画像';

CREATE TABLE IF NOT EXISTS xhs_kol_cooperation (
    coop_id VARCHAR(64) PRIMARY KEY,
    kol_id VARCHAR(64) NOT NULL,
    note_id VARCHAR(64) NOT NULL,
    coop_date DATE NOT NULL,
    coop_cost DECIMAL(18, 2) NOT NULL,
    expected_gmv DECIMAL(18, 2) NOT NULL,
    actual_gmv DECIMAL(18, 2) NOT NULL,
    status VARCHAR(32) NOT NULL
) COMMENT='小红书达人合作记录';

CREATE TABLE IF NOT EXISTS xhs_campaign_daily_metrics (
    metric_date DATE NOT NULL,
    campaign_id VARCHAR(64) NOT NULL,
    campaign_name VARCHAR(128) NOT NULL,
    spend DECIMAL(18, 2) NOT NULL,
    impressions BIGINT NOT NULL,
    clicks BIGINT NOT NULL,
    conversions BIGINT NOT NULL,
    gmv DECIMAL(18, 2) NOT NULL,
    PRIMARY KEY (metric_date, campaign_id)
) COMMENT='小红书广告投放日报';

CREATE TABLE IF NOT EXISTS xhs_product (
    product_id VARCHAR(64) PRIMARY KEY,
    product_name VARCHAR(128) NOT NULL,
    category VARCHAR(64) NOT NULL,
    price DECIMAL(18, 2) NOT NULL,
    status VARCHAR(32) NOT NULL
) COMMENT='小红书商品基础信息';

CREATE TABLE IF NOT EXISTS xhs_order (
    order_id VARCHAR(64) PRIMARY KEY,
    order_time DATETIME NOT NULL,
    product_id VARCHAR(64) NOT NULL,
    note_id VARCHAR(64),
    account_id VARCHAR(64),
    source_type VARCHAR(32) NOT NULL,
    quantity INT NOT NULL,
    order_amount DECIMAL(18, 2) NOT NULL,
    order_status VARCHAR(32) NOT NULL
) COMMENT='小红书订单数据';

