from __future__ import annotations

import re
from pathlib import Path


LATEST_TABLES_PATH = Path("taidou_local_life_tables.txt")
MAPPING_PATH = Path("../../Downloads/业务线_数仓表映射-1.md")
OUT_PATH = Path("table_mapping_diff.md")


def read_latest_tables() -> set[str]:
    return {
        line.strip()
        for line in LATEST_TABLES_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def read_mapping_tables() -> set[str]:
    text = MAPPING_PATH.read_text(encoding="utf-8")
    return set(re.findall(r"^\|\s*`([^`]+)`\s*\|", text, flags=re.MULTILINE))


def main() -> None:
    latest_tables = read_latest_tables()
    mapping_tables = read_mapping_tables()
    latest_not_in_mapping = sorted(latest_tables - mapping_tables)
    mapping_not_in_latest = sorted(mapping_tables - latest_tables)

    lines = [
        "# 最新数仓表清单与业务线映射差异",
        "",
        f"- 最新数仓表清单：{len(latest_tables)} 张",
        f"- `业务线_数仓表映射-1.md`：{len(mapping_tables)} 张",
        f"- 最新有但映射没有：{len(latest_not_in_mapping)} 张",
        f"- 映射有但最新没有：{len(mapping_not_in_latest)} 张",
        "",
        "## 最新有但 `-1.md` 映射没有",
        "",
    ]
    lines.extend(f"- `{table}`" for table in latest_not_in_mapping)
    lines.extend(["", "## `-1.md` 映射有但最新清单没有", ""])
    if mapping_not_in_latest:
        lines.extend(f"- `{table}`" for table in mapping_not_in_latest)
    else:
        lines.append("无")

    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"latest_count={len(latest_tables)}")
    print(f"mapping_count={len(mapping_tables)}")
    print(f"latest_not_in_mapping={len(latest_not_in_mapping)}")
    print(f"mapping_not_in_latest={len(mapping_not_in_latest)}")
    print(f"wrote {OUT_PATH}")
    print("latest_not_in_mapping:")
    for table in latest_not_in_mapping:
        print(table)
    print("mapping_not_in_latest:")
    for table in mapping_not_in_latest:
        print(table)


if __name__ == "__main__":
    main()