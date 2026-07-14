from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RANDOM_SEED = 20260714


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def daterange(days: int) -> list[date]:
    today = date.today()
    return [today - timedelta(days=offset) for offset in range(days - 1, -1, -1)]


def main() -> None:
    random.seed(RANDOM_SEED)
    days = daterange(30)
    categories = ["美妆", "穿搭", "家居", "母婴", "美食", "学习"]
    keywords = ["夏季穿搭", "防晒衣", "通勤包", "低卡晚餐", "收纳好物", "AI学习"]
    topics = ["夏日生活", "通勤穿搭", "好物分享", "效率提升", "新手指南"]
    content_types = ["image_text", "short_video", "live_replay"]
    source_types = ["organic", "kol_coop", "ad"]

    products = []
    for index, category in enumerate(categories, start=1):
        products.append(
            {
                "product_id": f"prod_{index:03d}",
                "product_name": f"{category}示例商品{index}",
                "category": category,
                "price": round(random.uniform(39, 399), 2),
                "status": "on_sale",
            }
        )

    kols = []
    for index in range(1, 16):
        follower_count = random.randint(8000, 800000)
        kols.append(
            {
                "kol_id": f"kol_{index:03d}",
                "kol_name": f"达人{index:02d}",
                "category": random.choice(categories),
                "follower_count": follower_count,
                "avg_like_count": int(follower_count * random.uniform(0.003, 0.02)),
                "avg_collect_count": int(follower_count * random.uniform(0.001, 0.012)),
                "quote_price": round(follower_count * random.uniform(0.015, 0.08), 2),
            }
        )

    notes = []
    for index in range(1, 61):
        publish_day = random.choice(days)
        content_type = random.choice(content_types)
        source_type = random.choices(source_types, weights=[0.55, 0.25, 0.2])[0]
        product = random.choice(products)
        kol = random.choice(kols) if source_type == "kol_coop" else None
        keyword = random.choice(keywords)
        notes.append(
            {
                "note_id": f"note_{index:04d}",
                "account_id": "acct_main_001",
                "note_title": f"{keyword}：{random.choice(['新手必看', '避坑指南', '实测分享', '高收藏清单'])}",
                "content_type": content_type,
                "publish_time": datetime.combine(publish_day, datetime.min.time()).replace(
                    hour=random.randint(8, 22),
                    minute=random.choice([0, 15, 30, 45]),
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "keyword_main": keyword,
                "topic": random.choice(topics),
                "product_id": product["product_id"],
                "kol_id": kol["kol_id"] if kol else "",
                "source_type": source_type,
                "note_url": f"https://www.xiaohongshu.com/explore/mock_{index:04d}",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    note_metrics = []
    for note in notes:
        publish = datetime.strptime(str(note["publish_time"]), "%Y-%m-%d %H:%M:%S").date()
        for metric_day in days:
            if metric_day < publish:
                continue
            age = max((metric_day - publish).days, 0)
            decay = max(0.15, 1 - age * 0.07)
            base_impressions = random.randint(600, 18000)
            if note["source_type"] == "ad":
                base_impressions *= 2
            if note["content_type"] == "short_video":
                base_impressions = int(base_impressions * 1.25)
            impressions = int(base_impressions * decay)
            clicks = int(impressions * random.uniform(0.04, 0.18))
            likes = int(impressions * random.uniform(0.01, 0.08))
            collects = int(impressions * random.uniform(0.005, 0.06))
            comments = int(impressions * random.uniform(0.001, 0.015))
            shares = int(impressions * random.uniform(0.001, 0.012))
            follows = int(impressions * random.uniform(0.0005, 0.006))
            orders = int(clicks * random.uniform(0.002, 0.04))
            product_price = next(p["price"] for p in products if p["product_id"] == note["product_id"])
            note_metrics.append(
                {
                    "metric_date": metric_day.isoformat(),
                    "note_id": note["note_id"],
                    "impressions": impressions,
                    "clicks": clicks,
                    "likes": likes,
                    "collects": collects,
                    "comments": comments,
                    "shares": shares,
                    "follows": follows,
                    "orders": orders,
                    "gmv": round(orders * float(product_price) * random.uniform(0.8, 1.2), 2),
                }
            )

    account_metrics = []
    followers = 18000
    for metric_day in days:
        new_followers = random.randint(20, 360)
        followers += new_followers
        account_metrics.append(
            {
                "metric_date": metric_day.isoformat(),
                "account_id": "acct_main_001",
                "followers": followers,
                "new_followers": new_followers,
                "profile_views": random.randint(500, 6000),
                "total_impressions": random.randint(20000, 180000),
                "total_interactions": random.randint(800, 9000),
            }
        )

    keyword_trends = []
    for metric_day in days:
        for keyword in keywords:
            keyword_trends.append(
                {
                    "metric_date": metric_day.isoformat(),
                    "keyword_name": keyword,
                    "search_index": random.randint(1000, 80000),
                    "note_count": random.randint(100, 12000),
                    "avg_interaction_rate": round(random.uniform(0.015, 0.18), 6),
                }
            )

    cooperations = []
    coop_notes = [note for note in notes if note["source_type"] == "kol_coop"]
    for index, note in enumerate(coop_notes[:20], start=1):
        kol = next(kol for kol in kols if kol["kol_id"] == note["kol_id"])
        cost = float(kol["quote_price"]) * random.uniform(0.7, 1.2)
        actual_gmv = cost * random.uniform(0.3, 3.5)
        cooperations.append(
            {
                "coop_id": f"coop_{index:04d}",
                "kol_id": note["kol_id"],
                "note_id": note["note_id"],
                "coop_date": str(note["publish_time"])[:10],
                "coop_cost": round(cost, 2),
                "expected_gmv": round(cost * 1.5, 2),
                "actual_gmv": round(actual_gmv, 2),
                "status": "finished",
            }
        )

    campaign_metrics = []
    campaign_names = ["夏季穿搭搜索推广", "防晒衣信息流", "AI学习人群定向"]
    for metric_day in days:
        for index, campaign_name in enumerate(campaign_names, start=1):
            spend = random.uniform(100, 3000)
            impressions = random.randint(8000, 180000)
            clicks = int(impressions * random.uniform(0.015, 0.08))
            conversions = int(clicks * random.uniform(0.01, 0.12))
            campaign_metrics.append(
                {
                    "metric_date": metric_day.isoformat(),
                    "campaign_id": f"camp_{index:03d}",
                    "campaign_name": campaign_name,
                    "spend": round(spend, 2),
                    "impressions": impressions,
                    "clicks": clicks,
                    "conversions": conversions,
                    "gmv": round(conversions * random.uniform(80, 360), 2),
                }
            )

    orders = []
    order_index = 1
    for metric in note_metrics:
        for _ in range(int(metric["orders"])):
            note = next(note for note in notes if note["note_id"] == metric["note_id"])
            product = next(p for p in products if p["product_id"] == note["product_id"])
            quantity = random.randint(1, 3)
            orders.append(
                {
                    "order_id": f"order_{order_index:06d}",
                    "order_time": f"{metric['metric_date']} {random.randint(8, 23):02d}:{random.choice([0, 15, 30, 45]):02d}:00",
                    "product_id": product["product_id"],
                    "note_id": note["note_id"],
                    "account_id": note["account_id"],
                    "source_type": note["source_type"],
                    "quantity": quantity,
                    "order_amount": round(quantity * float(product["price"]) * random.uniform(0.85, 1.0), 2),
                    "order_status": random.choice(["paid", "shipped", "completed"]),
                }
            )
            order_index += 1

    write_csv(DATA_DIR / "xhs_product.csv", products)
    write_csv(DATA_DIR / "xhs_kol_profile.csv", kols)
    write_csv(DATA_DIR / "xhs_note.csv", notes)
    write_csv(DATA_DIR / "xhs_note_daily_metrics.csv", note_metrics)
    write_csv(DATA_DIR / "xhs_account_daily_metrics.csv", account_metrics)
    write_csv(DATA_DIR / "xhs_keyword_trend.csv", keyword_trends)
    write_csv(DATA_DIR / "xhs_kol_cooperation.csv", cooperations)
    write_csv(DATA_DIR / "xhs_campaign_daily_metrics.csv", campaign_metrics)
    write_csv(DATA_DIR / "xhs_order.csv", orders)

    print(f"Generated XHS mock data in: {DATA_DIR}")


if __name__ == "__main__":
    main()

