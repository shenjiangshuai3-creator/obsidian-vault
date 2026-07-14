---
title: Deep Agents人员数据质量项目实操
created: 2026-07-14
tags:
  - LangChain
  - DeepAgents
  - Agent
  - 数据质量
  - 项目实操
status: planned
---

# Deep Agents 人员数据质量项目实操

> [!summary] 项目定位
> 使用 Deep Agents 构建“人员数据质量调查 Agent”，综合练习任务规划、工具调用、虚拟文件系统、专业子代理、上下文管理和人工审批。

## 一、为什么选择这个项目

相比天气查询等单工具 Demo，人员数据质量调查是一个真实的多步骤任务：它需要读取多个数据源、分析表结构、执行数据检查、判断异常原因、生成报告，并在修改数据前等待人工审批。

这个项目与现有的飞书、AnyCross 和 MySQL 数据同步工作能够直接结合，也适合作为 AI 解决方案工程师的项目案例。

## 二、项目目标

用户输入：

> 检查 2026-07-14 飞书同步数据与 MySQL 人员数据的差异，分析原因，生成报告，但不要直接修改数据库。

Agent 自动完成：

```text
制定检查计划
→ 分析表结构和字段映射
→ 执行只读数据检查
→ 委派专业子代理分析异常
→ 汇总证据和修复建议
→ 生成 Markdown 报告
→ 修改数据前等待人工审批
```

最终生成：

```text
reports/2026-07-14-人员数据质量报告.md
```

## 三、Deep Agents 能力映射

| Deep Agents 能力 | 项目中的应用 |
|---|---|
| Task Planning | 自动拆分数据检查任务 |
| Tools | 查询表结构、执行只读 SQL、读取同步日志 |
| Virtual Filesystem | 保存中间结果和最终报告 |
| Subagents | 分别处理结构、数据和业务规则 |
| Context Offloading | 将大量查询结果写入文件，避免主上下文膨胀 |
| Memory | 记住字段映射和历史异常规则 |
| Human-in-the-loop | 修改数据前暂停并等待审批 |
| LangSmith | 查看规划、工具调用和子代理执行过程 |

## 四、项目目录

```text
deep-agent-data-quality/
├── agent.py
├── tools.py
├── fixtures/
│   ├── feishu_users.csv
│   └── mysql_users.csv
├── knowledge/
│   ├── field_mapping.md
│   └── quality_rules.md
├── reports/
├── evals/
│   └── cases.jsonl
├── tests/
├── .env.example
└── requirements.txt
```

第一版使用 CSV 模拟数据。流程跑通后，再替换为飞书 API 和 MySQL 只读账号。

## 五、Agent 架构

```text
                    ┌────────────────────┐
                    │  主 Agent / 负责人  │
                    │  规划、委派、汇总   │
                    └─────────┬──────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │结构分析子代理│ │数据分析子代理│ │规则审计子代理│
      │字段及表映射  │ │空值重复分布  │ │原因及影响判断│
      └──────────────┘ └──────────────┘ └──────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                    Markdown 数据质量报告
                              │
                              ▼
                    人工审批后执行修复
```

### 主 Agent 职责

- 理解用户目标并制定检查计划
- 判断何时调用工具或委派子代理
- 汇总各子代理的精简结论
- 要求所有结论提供查询证据
- 将最终报告写入 `reports` 目录
- 未经批准不允许修改数据库

### 专业子代理

| 子代理 | 职责 | 最小工具集 |
|---|---|---|
| `schema-analyst` | 分析表结构、主键、字段映射和约束差异 | `get_table_schema` |
| `data-profiler` | 检查数量、空值、重复值和状态分布 | `profile_employee_data`、`inspect_sync_logs` |
| `rule-auditor` | 根据质量规则判断影响并提出修复建议 | 读取规则文件、读取分析结果 |

子代理只拥有完成自身任务所需要的工具，避免所有子代理共享完整权限。

## 六、环境准备

### 安装依赖

```bash
pip install deepagents langchain langgraph python-dotenv
```

连接 MySQL 时再安装：

```bash
pip install sqlalchemy pymysql sqlglot
```

还需要安装所选模型供应商对应的 LangChain 集成包。Deep Agents 要求模型支持 Tool Calling。

### 环境变量

`.env.example`：

```dotenv
MODEL_NAME=provider:model
MODEL_API_KEY=your-api-key

# 第二阶段再启用
MYSQL_URL=mysql+pymysql://readonly_user:password@host:3306/database

# 可选：LangSmith观测
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-api-key
```

不要将真实密钥提交到 Git。

## 七、核心代码框架

```python
import os
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver

ROOT = Path(__file__).parent.resolve()


@tool
def get_table_schema(table_name: str) -> str:
    """查询指定业务表的字段、类型、主键和索引。"""
    # 第一版读取 fixtures/schema.json
    # 第二版查询 information_schema
    return f"Schema information for {table_name}"


@tool
def profile_employee_data(snapshot_date: str) -> str:
    """执行只读人员数据检查，返回数量、空值、重复和状态分布。"""
    return """
    飞书人员数：100
    MySQL人员数：98
    缺失人员：2
    重复手机号：1
    部门为空：3
    """


@tool
def inspect_sync_logs(snapshot_date: str) -> str:
    """读取指定日期的同步日志和失败记录。"""
    return "发现2条数据因部门编码不存在而同步失败"


@tool
def apply_fix(fix_plan: str) -> str:
    """根据已审批的修复计划修改数据。"""
    # 学习阶段只返回模拟结果，不真正修改数据库
    return f"DEMO：已接收修复计划：{fix_plan}"


subagents = [
    {
        "name": "schema-analyst",
        "description": "分析飞书与MySQL表结构、字段映射和约束差异。",
        "system_prompt": (
            "你是数据模型分析师。只分析结构和字段映射，"
            "输出发现、证据、风险，不执行任何数据修改。"
        ),
        "tools": [get_table_schema],
    },
    {
        "name": "data-profiler",
        "description": "检查人员数据数量、空值、重复值和异常分布。",
        "system_prompt": (
            "你是数据质量分析师。使用工具获取统计结果，"
            "输出异常类型、数量、证据和可能原因。"
        ),
        "tools": [profile_employee_data, inspect_sync_logs],
    },
]


agent = create_deep_agent(
    model=os.environ["MODEL_NAME"],
    tools=[
        get_table_schema,
        profile_employee_data,
        inspect_sync_logs,
        apply_fix,
    ],
    subagents=subagents,
    backend=FilesystemBackend(root_dir=str(ROOT)),
    system_prompt="""
你是人员数据质量调查负责人。

必须先制定计划，再委派专业子代理。
所有结论必须包含工具查询证据。
大量中间结果写入文件，避免上下文膨胀。
最终使用 write_file 将报告写入 reports 目录。
未经人工批准，不得调用 apply_fix。
""",
    interrupt_on={
        "apply_fix": {
            "allowed_decisions": ["approve", "reject"]
        }
    },
    checkpointer=MemorySaver(),
)
```

## 八、运行 Agent

```python
result = agent.invoke(
    {
        "messages": [{
            "role": "user",
            "content": (
                "检查2026-07-14飞书与MySQL人员数据差异，"
                "分析原因并生成Markdown报告，不要修改数据库。"
            ),
        }]
    },
    config={
        "configurable": {
            "thread_id": "employee-check-20260714"
        }
    },
)

print(result["messages"][-1].content)
```

人工审批流程需要持续使用同一个 `thread_id`。当 `apply_fix` 被调用时，Agent 会暂停，等待批准或拒绝。

## 九、数据质量规则

第一版至少实现以下检查：

| 规则 | 检查内容 | 示例 |
|---|---|---|
| 数量一致性 | 飞书与 MySQL 有效人员数量是否一致 | 飞书 100，MySQL 98 |
| 唯一性 | 员工 ID、手机号是否重复 | 同一手机号出现两次 |
| 完整性 | 部门、岗位、状态等必填字段是否为空 | 部门编码为空 |
| 枚举合法性 | 人员状态是否属于允许范围 | 出现未知状态 |
| 引用完整性 | 人员部门是否能关联到有效部门 | 部门编码不存在 |
| 同步及时性 | 数据更新时间是否超过允许延迟 | 飞书已更新但 MySQL 未更新 |

## 十、安全设计

### 第一阶段

- 只使用 CSV 模拟数据
- `apply_fix` 只返回模拟结果
- Agent 只能在项目根目录下读写文件

### 接入数据库后

- MySQL 使用独立只读账号
- 查询工具只允许 `SELECT` 和受控元数据查询
- 使用 SQL 解析器检查语句，不依赖简单字符串判断
- 设置查询超时、最大返回行数和允许访问的表白名单
- 禁止 Agent 直接获得数据库密码
- 写入操作使用独立工具，并配置人工审批
- 记录查询、参数、审批人和执行结果

> [!warning] 权限原则
> Prompt 不能替代后端权限控制。即使提示词要求“只读”，数据库账号和工具层仍然必须真正限制写入能力。

## 十一、分阶段完成

### 第 1 阶段：基础版

- 使用两份 CSV 模拟飞书和 MySQL 数据
- 使用单个 Agent 完成检查
- 生成 Markdown 数据质量报告

### 第 2 阶段：工具版

- 增加表结构查询工具
- 增加数据统计工具
- 增加同步日志查询工具
- 为工具编写单元测试

### 第 3 阶段：Deep Agent 版

- 加入 `schema-analyst` 子代理
- 加入 `data-profiler` 子代理
- 使用虚拟文件系统保存中间结果
- 验证主 Agent 只收到子代理的精简结论

### 第 4 阶段：安全版

- 接入 MySQL 只读账号
- 配置路径权限和数据库表白名单
- 修复操作加入 Human-in-the-loop
- 增加操作审计日志

### 第 5 阶段：生产版

- 使用 LangSmith Trace 观察调用链路
- 建立固定评测集和回归测试
- 增加超时、重试、并发和成本监控
- 将 Agent 封装为 FastAPI 或内部 Web 应用

## 十二、验收标准

- [ ] 能识别缺失、重复、空值、状态和部门映射异常
- [ ] 每个异常结论都包含数据证据
- [ ] 报告包含问题、影响、原因和修复建议
- [ ] 大量中间结果能够写入文件，不挤占主上下文
- [ ] 主 Agent 能正确委派专业子代理
- [ ] 未经人工审批不能执行修复
- [ ] 使用固定异常样例进行回归测试
- [ ] 能查看完整的 Agent、工具和子代理调用链路

## 十三、最终交付物

```text
可运行的人员数据质量 Agent
+ 飞书/MySQL 数据查询工具
+ 专业子代理配置
+ Markdown 数据质量报告
+ 人工审批流程
+ 自动化测试与评测集
+ Docker 和环境配置
+ 使用、部署及安全说明
```

## 官方文档

- [Deep Agents Overview](https://docs.langchain.com/oss/python/deepagents/overview)
- [Deep Agents Quickstart](https://docs.langchain.com/oss/python/deepagents/quickstart)
- [Subagents](https://docs.langchain.com/oss/python/deepagents/subagents)
- [Human-in-the-loop](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop)
- [Backends](https://docs.langchain.com/oss/python/deepagents/backends)
- [Going to production](https://docs.langchain.com/oss/python/deepagents/going-to-production)

## 相关笔记

- [[LangChain学习笔记]]
- [[01-学习路线与核心内容]]
- [[AI解决方案工程师能力图谱与学习路线]]
- [[飞书API到MySQL数仓落库方案]]

