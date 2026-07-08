from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


TABLE_LIST_PATH = Path("taidou_local_life_tables.txt")
MAPPING_PATHS = [
    Path("../../Downloads/业务线_数仓表映射-1.md"),
    Path("../../Downloads/业务线_数仓表映射.md"),
]
OUT_CSV = Path("table_asset_inventory.csv")
OUT_MD = Path("table_asset_inventory_summary.md")


BUSINESS_CODE_BY_NAME = {
    "职能后台": "admin",
    "内容创意": "content",
    "投流/投放": "traffic",
    "直播": "live",
    "达人": "talent",
    "销售/商业化": "sales",
    "本地通": "xdbdt",
    "本地生活": "local_life",
    "技术研发": "tech",
    "培训": "training",
}


DOMAIN_RULES = [
    ("日志/任务/系统", ["log", "event", "task", "run", "checkpoint", "history", "migration", "flyway", "日志", "任务", "历史"]),
    ("订单交易", ["order", "trade", "verify", "pay", "refund", "poi_order", "订单", "交易", "核销", "支付", "退款"]),
    ("线索/私信/客户", ["clue", "im", "message", "intention", "customer", "client", "wechat", "线索", "私信", "客户", "意向"]),
    ("直播", ["live", "room", "直播"]),
    ("视频/内容/素材", ["video", "content", "material", "script", "creative", "douyin_hot", "素材", "视频", "内容", "脚本"]),
    ("达人/作者", ["talent", "influencer", "author", "bloger", "creator", "达人", "作者", "博主"]),
    ("广告/投放", ["ad", "ads", "advert", "ocean", "qianchuan", "promotion", "bidding", "投放", "广告", "营销"]),
    ("门店/经销商/POI", ["store", "dealer", "shop", "merchant", "poi", "门店", "经销商", "商家"]),
    ("汽车/品牌/车型", ["car", "brand", "series", "model", "vehicle", "汽车", "品牌", "车型", "车系"]),
    ("组织/用户/权限", ["user", "account", "role", "dept", "group", "organization", "sys", "用户", "账号", "组织", "权限", "角色"]),
    ("AI/知识库/机器人", ["ai", "kb", "knowledge", "prompt", "bot", "agent", "coze", "lumax", "llm", "知识库", "机器人"]),
    ("财务/成本/结算", ["finance", "cost", "amount", "settle", "bill", "quota", "token", "财务", "成本", "结算", "金额"]),
]


def tokenize(text: str) -> set[str]:
    return {token for token in re.split(r"[^0-9a-zA-Z\u4e00-\u9fff]+", text.lower()) if token}


def read_tables() -> list[str]:
    return [line.strip() for line in TABLE_LIST_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_mapping() -> dict[str, dict[str, str]]:
    mapping_path = next((path for path in MAPPING_PATHS if path.exists()), None)
    if not mapping_path:
        return {}

    current_business = "未映射"
    result: dict[str, dict[str, str]] = {}
    section_re = re.compile(r"^##\s+(.+?)\s+\(`([^`]+)`\)")
    row_re = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|")

    for line in mapping_path.read_text(encoding="utf-8").splitlines():
        section_match = section_re.match(line)
        if section_match:
            current_business = section_match.group(1).strip()
            continue

        row_match = row_re.match(line)
        if not row_match:
            continue

        table_name, comment = row_match.groups()
        comment = "" if comment.strip() == "-" else comment.strip()
        result[table_name] = {
            "business_line": current_business,
            "business_code": BUSINESS_CODE_BY_NAME.get(current_business, "unknown"),
            "comment": comment,
        }
    return result


def layer_of(table: str) -> str:
    prefix = table.split("_", 1)[0].lower() if "_" in table else "other"
    return prefix if prefix in {"ods", "dwd", "dws", "ads", "dim", "tmp", "stg", "mid", "app"} else "other"


def domain_of(table: str, comment: str) -> str:
    text = f"{table} {comment}".lower()
    tokens = tokenize(text)
    for domain, keywords in DOMAIN_RULES:
        if any(keyword.lower() in tokens or keyword.lower() in comment.lower() for keyword in keywords):
            return domain
    return "未分类"


def main() -> None:
    tables = read_tables()
    mapping = parse_mapping()
    rows = []

    for table in tables:
        mapped = mapping.get(table, {})
        comment = mapped.get("comment", "")
        business_line = mapped.get("business_line", "未映射")
        business_code = mapped.get("business_code", "unmapped")
        layer = layer_of(table)
        domain = domain_of(table, comment)
        rows.append({
            "table_name": table,
            "layer": layer,
            "business_line": business_line,
            "business_code": business_code,
            "domain": domain,
            "comment": comment,
        })

    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["table_name", "layer", "business_line", "business_code", "domain", "comment"])
        writer.writeheader()
        writer.writerows(rows)

    layer_counts = Counter(row["layer"] for row in rows)
    business_counts = Counter(row["business_line"] for row in rows)
    domain_counts = Counter(row["domain"] for row in rows)
    unmapped = [row for row in rows if row["business_line"] == "未映射"]
    no_comment = [row for row in rows if not row["comment"]]
    samples_by_domain: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        if len(samples_by_domain[row["domain"]]) < 8:
            samples_by_domain[row["domain"]].append(row["table_name"])

    lines = [
        "# 数仓表资产第一轮分类盘点",
        "",
        "## 结论摘要",
        "",
        f"- 本地表清单总数：{len(rows)} 张",
        f"- 已匹配业务线映射：{len(rows) - len(unmapped)} 张",
        f"- 未匹配业务线映射：{len(unmapped)} 张",
        f"- 缺少中文说明/注释：{len(no_comment)} 张",
        "",
        "## 按数仓分层统计",
        "",
        "| 分层 | 表数 |",
        "|---|---:|",
    ]
    lines.extend(f"| {name} | {count} |" for name, count in layer_counts.most_common())

    lines.extend(["", "## 按业务线统计", "", "| 业务线 | 表数 |", "|---|---:|"])
    lines.extend(f"| {name} | {count} |" for name, count in business_counts.most_common())

    lines.extend(["", "## 按主题域统计", "", "| 主题域 | 表数 | 样例 |", "|---|---:|---|"])
    for name, count in domain_counts.most_common():
        samples = ", ".join(f"`{item}`" for item in samples_by_domain[name])
        lines.append(f"| {name} | {count} | {samples} |")

    lines.extend(["", "## 优先处理建议", ""])
    lines.extend([
        "1. 先处理 `订单交易`、`线索/私信/客户`、`直播`、`视频/内容/素材`、`广告/投放` 五类，它们更接近常用业务分析和报表需求。",
        "2. 对每个主题域分批读取字段元数据，每批控制在 20-40 张表，避免一次性扫描 MaxCompute 元数据时间过长。",
        "3. 对 `未分类`、`未映射`、缺少注释的表单独做二次识别，优先补表说明和负责人/业务线。",
        "4. 月份后缀、历史表、临时表先归并为同一逻辑表族，避免资产口径被重复表膨胀。",
    ])

    if unmapped:
        lines.extend(["", "## 未匹配业务线样例", ""])
        lines.extend(f"- `{row['table_name']}`" for row in unmapped[:30])

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")
    print(f"tables={len(rows)} mapped={len(rows) - len(unmapped)} unmapped={len(unmapped)} no_comment={len(no_comment)}")


if __name__ == "__main__":
    main()