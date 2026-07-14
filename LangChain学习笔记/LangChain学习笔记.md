---
created: 2026-07-14
tags:
  - LangChain
  - AI应用开发
  - Agent
  - RAG
  - 面试
---

# LangChain 学习笔记

> 目标：系统掌握 LangChain 的核心概念、RAG 应用、Agent 工具调用、LangGraph 编排和工程化落地，并能应对 AI 应用开发相关面试。

## 目录

- [[01-学习路线与核心内容|01-学习路线与核心内容]]
- [[02-面试题|02-面试题]]
- [[03-Deep Agents人员数据质量项目实操|03-Deep Agents人员数据质量项目实操]]
- [[04-本地数据问答Deep Agent项目拆解与面试回答|04-本地数据问答Deep Agent项目拆解与面试回答]]

## 推荐学习顺序

1. 先理解 LangChain 是什么：它不是大模型本身，而是把模型、Prompt、工具、检索、记忆、工作流串起来的应用开发框架。
2. 再掌握基础组件：Chat Model、Prompt Template、Output Parser、Tool、Retriever。
3. 重点学习 RAG：文档加载、切分、Embedding、向量库、检索、重排、生成、评估。
4. 学习 Agent：模型如何决定调用工具，工具 schema 如何设计，如何控制错误和循环。
5. 学习 LangGraph：当 Agent 流程需要状态、分支、循环、人工审核时，用图来编排。
6. 最后补齐工程化：LangSmith 调试观测、评估集、成本控制、权限与安全。

## 当前重点版本认知

LangChain 现在更强调：

- `create_agent`：快速创建具备工具调用能力的 Agent。
- LangGraph：用于更复杂、更可控的 Agent 工作流。
- RAG：依然是企业知识库、数据问答、文档助手的高频场景。
- LangSmith：用于 trace、debug、评估和线上观测。

## 官方资料

- [LangChain Python overview](https://docs.langchain.com/oss/python/langchain/overview)
- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)
- [LangChain retrieval](https://docs.langchain.com/oss/python/langchain/retrieval)
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangSmith docs](https://docs.smith.langchain.com/)

## 学习产出建议

每学完一个模块，至少沉淀三类内容：

| 类型 | 产出 |
|---|---|
| 概念笔记 | 这个组件解决什么问题、什么时候用、有什么坑 |
| 代码模板 | 最小可运行 demo，保留依赖和关键参数 |
| 面试复盘 | 用自己的话解释原理，并准备一个项目案例 |
