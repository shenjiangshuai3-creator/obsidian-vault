"""CLI Agent for generating MaxCompute SQL with LangChain.

The agent uses OpenAI for reasoning and PyODPS for MaxCompute metadata lookup.
It is intentionally read-only: tools inspect table names, schemas, and SELECT SQL
validity, but do not execute data modification statements.
"""

from __future__ import annotations

import argparse
import os
from typing import Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from odps import ODPS


SYSTEM_PROMPT = """你是一个面向阿里云 MaxCompute 的 SQL 生成 Agent。

你的目标是根据用户的中文业务问题，自动检索 MaxCompute 元数据，并生成可执行、可审阅的 MaxCompute SQL。

工作规则：
1. 优先使用工具查找相关表和字段，不要凭空编造表结构。
2. 如果用户没有指定表名，先根据关键词搜索表；如果仍不确定，列出候选表并说明假设。
3. 生成 SQL 必须符合 MaxCompute SQL 方言。
4. 分区表查询时优先添加分区条件；如果用户未给日期，用 ${bizdate} 占位符并提示替换。
5. 默认只生成 SELECT 查询；不要生成 INSERT、UPDATE、DELETE、DROP、TRUNCATE 等写操作，除非用户明确要求且再次确认。
6. 输出必须包含：使用到的表、关键字段、SQL、口径/假设说明、需要确认的风险点。
"""


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_odps_client() -> ODPS:
    return ODPS(
        get_required_env("ODPS_ACCESS_ID"),
        get_required_env("ODPS_ACCESS_KEY"),
        get_required_env("ODPS_PROJECT"),
        endpoint=get_required_env("ODPS_ENDPOINT"),
    )


@tool
def list_maxcompute_tables(prefix: Optional[str] = None, limit: int = 50) -> str:
    """List MaxCompute table names. Use prefix to narrow the result when possible."""
    odps = get_odps_client()
    tables: list[str] = []
    for table in odps.list_tables(prefix=prefix):
        tables.append(table.name)
        if len(tables) >= limit:
            break
    return "\n".join(tables) if tables else "No tables found."


@tool
def search_maxcompute_tables(keyword: str, limit: int = 50) -> str:
    """Search MaxCompute table names by keyword."""
    odps = get_odps_client()
    keyword_lower = keyword.lower()
    matches: list[str] = []
    for table in odps.list_tables():
        if keyword_lower in table.name.lower():
            matches.append(table.name)
            if len(matches) >= limit:
                break
    return "\n".join(matches) if matches else f"No tables matched keyword: {keyword}"


@tool
def describe_maxcompute_table(table_name: str) -> str:
    """Describe a MaxCompute table schema, including columns, comments, and partitions."""
    odps = get_odps_client()
    if not odps.exist_table(table_name):
        return f"Table not found: {table_name}"

    table = odps.get_table(table_name)
    schema = table.table_schema
    lines = [f"Table: {table_name}"]

    if table.comment:
        lines.append(f"Comment: {table.comment}")

    lines.append("Columns:")
    for column in schema.simple_columns:
        comment = f" -- {column.comment}" if column.comment else ""
        lines.append(f"- {column.name} {column.type}{comment}")

    if schema.partitions:
        lines.append("Partitions:")
        for partition in schema.partitions:
            comment = f" -- {partition.comment}" if partition.comment else ""
            lines.append(f"- {partition.name} {partition.type}{comment}")

    return "\n".join(lines)


@tool
def explain_maxcompute_select(sql: str) -> str:
    """Run EXPLAIN for a SELECT query to check whether MaxCompute accepts the SQL."""
    normalized = sql.strip().rstrip(";")
    if not normalized.lower().startswith("select"):
        return "Rejected: this tool only explains SELECT SQL."

    try:
        odps = get_odps_client()
        instance = odps.execute_sql("EXPLAIN " + normalized)
        instance.wait_for_success()
        return "EXPLAIN succeeded. MaxCompute accepted the SELECT syntax."
    except Exception as exc:  # noqa: BLE001
        return f"EXPLAIN failed: {type(exc).__name__}: {exc}"


def build_agent():
    load_dotenv()
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    model = ChatOpenAI(model=model_name, temperature=0)
    tools = [
        list_maxcompute_tables,
        search_maxcompute_tables,
        describe_maxcompute_table,
        explain_maxcompute_select,
    ]
    return create_agent(model=model, tools=tools, system_prompt=SYSTEM_PROMPT)


def extract_final_text(agent_result: object) -> str:
    if not isinstance(agent_result, dict):
        return str(agent_result)

    messages = agent_result.get("messages")
    if not messages:
        return str(agent_result)

    final_message = messages[-1]
    content = getattr(final_message, "content", final_message)
    if isinstance(content, list):
        return "\n".join(str(item) for item in content)
    return str(content)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MaxCompute SQL with a LangChain CLI Agent.")
    parser.add_argument("question", nargs="*", help="中文 SQL 需求，例如：统计某表每天项目数")
    args = parser.parse_args()

    question = " ".join(args.question).strip()
    if not question:
        question = input("请输入 SQL 需求：").strip()

    agent = build_agent()
    result = agent.invoke({"messages": [HumanMessage(content=question)]})
    print("\n===== Agent 输出 =====")
    print(extract_final_text(result))


if __name__ == "__main__":
    main()
