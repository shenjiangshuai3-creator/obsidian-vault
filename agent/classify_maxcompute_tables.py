from collections import Counter, defaultdict
import os

from odps import ODPS


PROJECT = "test_taidou_local_life_dw"
ENDPOINT = "https://service.cn-shanghai.maxcompute.aliyun.com/api"


def main():
    access_id = os.environ["ODPS_ACCESS_ID"]
    access_key = os.environ["ODPS_ACCESS_KEY"]
    odps = ODPS(access_id, access_key, PROJECT, endpoint=ENDPOINT)

    tables = []
    for table in odps.list_tables():
        comment = ""
        try:
            comment = table.comment or ""
        except Exception:
            pass
        tables.append((table.name, comment))

    layers = ["ods", "dwd", "dws", "ads", "dim", "tmp", "stg", "mid", "app"]
    layer_counter = Counter()
    layer_samples = defaultdict(list)
    for name, _comment in sorted(tables):
        prefix = name.split("_", 1)[0].lower() if "_" in name else "other"
        layer = prefix if prefix in layers else "other"
        layer_counter[layer] += 1
        if len(layer_samples[layer]) < 6:
            layer_samples[layer].append(name)

    domains = {
        "订单交易": ["order", "trade", "pay", "payment", "refund", "settle", "核销", "订单", "交易", "支付", "退款"],
        "商品": ["product", "goods", "sku", "item", "spu", "商品", "产品"],
        "达人/作者": ["influencer", "author", "talent", "达人", "博主"],
        "视频/内容/素材": ["video", "content", "material", "素材", "视频", "内容"],
        "广告/营销": ["ad_", "_ad", "advert", "marketing", "campaign", "promotion", "广告", "投放", "营销"],
        "门店/商家": ["shop", "store", "merchant", "门店", "店铺", "商家"],
        "用户/会员": ["user", "member", "customer", "用户", "会员", "客户"],
        "POI/本地生活": ["poi", "local", "life", "本地生活"],
        "券/优惠": ["coupon", "voucher", "券", "优惠"],
        "直播": ["live", "room", "直播"],
        "财务/结算": ["finance", "account", "bill", "cost", "amount", "settlement", "财务", "账单", "成本", "金额"],
        "日志/事件": ["log", "event", "track", "日志", "埋点", "事件"],
    }

    domain_counter = Counter()
    domain_samples = defaultdict(list)
    for name, comment in sorted(tables):
        text = f"{name} {comment}".lower()
        matched = False
        for domain, keywords in domains.items():
            if any(keyword.lower() in text for keyword in keywords):
                domain_counter[domain] += 1
                matched = True
                if len(domain_samples[domain]) < 6:
                    domain_samples[domain].append(name)
        if not matched:
            domain_counter["未分类"] += 1
            if len(domain_samples["未分类"]) < 6:
                domain_samples["未分类"].append(name)

    print(f"TOTAL\t{len(tables)}")
    print("LAYER_COUNTS")
    for key, value in layer_counter.most_common():
        print(f"{key}\t{value}\t{', '.join(layer_samples[key])}")
    print("DOMAIN_COUNTS")
    for key, value in domain_counter.most_common():
        print(f"{key}\t{value}\t{', '.join(domain_samples[key])}")


if __name__ == "__main__":
    main()