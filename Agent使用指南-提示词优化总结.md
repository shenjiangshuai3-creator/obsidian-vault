# Agent 使用指南 - 提示词优化总结

> 基于实际使用过程中的经验总结，旨在提高 AI 执行准确性和减少人工干预

---

## 一、环境配置类提示词

### 1.1 文件路径问题

| 问题 | 解决方案 |
|------|---------|
| AI 读不到文件（路径不存在） | 尽量用**相对路径**或**完整绝对路径**，避免中文空格等特殊字符 |
| Obsidian Vault 中的文件 | 指定目录：`C:\Users\EDY\Documents\Obsidian Vault\xxx` |

### 1.2 Git 配置

```powershell
# 配置代理（访问 GitHub 时必须）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 配置身份信息
git config --global user.name "shenjiangshuai3-creator"
git config --global user.email "shenjiangshuai3@gmail.com"
```

### 1.3 VS Code Continue 插件

| 设置项 | 值 | 说明 |
|--------|----|------|
| `continue.enableAcceptConfirmation` | `false` | 关闭 Accept 确认，让 AI 自动执行 |

---

## 二、Obsidian 笔记管理类提示词

### 2.1 创建笔记

**推荐的提问方式：**
> "帮我在 Obsidian 中创建一篇 xxx 笔记，存入 Python学习笔记/01-基础知识 目录"

**AI 会执行：**
1. 创建 `.md` 文件
2. 添加 YAML front matter（created, tags）
3. 写入 Markdown 内容
4. `git add → commit → push` 到 GitHub

### 2.2 修改笔记

**推荐的提问方式：**
> "帮我把 xxx 笔记中的 xxx 内容修改为 xxx"

**注意：** AI 修改后可能会覆盖你在 Obsidian 中手动编辑的内容，建议：
- 在笔记中开辟 **「个性化修改记录」** 区域
- 或者告诉 AI "保留我之前的个性化修改"

### 2.3 同步到 GitHub

```powershell
cd C:\Users\EDY\Documents\"Obsidian Vault"
git add .
git commit -m "更新笔记"
git push
```

或双击 `sync_notes.bat` 一键同步。

---

## 三、SQL 相关提示词

### 3.1 生成 ER 图

**推荐的提问方式：**
> "根据这段 SQL，帮我生成 ER 图，连线标注字段=字段的格式"
>
> ```sql
> SELECT ... FROM A JOIN B ON A.id = B.a_id
> ```

**AI 会生成：**
- Mermaid ER 图
- 关联关系速查表
- 数据血缘图

### 3.2 数据探查

**推荐的提问方式：**
> "帮我写探查 xxx 表的 SQL，包括重复检查、空值检查、数据分布"

**AI 会生成：**
- 重复数据检查
- 空值统计
- 数据分布分析
- 跨表一致性验证
- 一键探查汇总

### 3.3 ER 图注意事项

| 容易出错的地方 | 正确做法 |
|---------------|---------|
| 连线关系用文字描述 | 改为 `字段1 = 字段2` 格式 |
| `data_syj_talent_video` 和 ODS 层重表 | 标注为同一业务不同分层 |
| 结果表画 has 关系线 | 改为数据血缘图展示写入关系 |

---

## 四、常见报错及解决

### 4.1 Git 连接失败
```
fatal: unable to access ... Failed to connect to github.com:443
```
**解决：** 配置代理 `git config --global http.proxy http://127.0.0.1:7890`

### 4.2 Python 执行时反引号转义问题
PowerShell 传递 Python 代码时，**反引号 ` 和引号 " 容易出错**。
**解决：** 
- 尽量用文件方式执行（创建 `.py` 文件再运行）
- 避免在命令行中写复杂 Python 代码

### 4.3 Obsidian Mermaid 不渲染
**原因：** 代码块用了单反引号 ` 而不是三个反引号 ```
**解决：** 确保使用 ` ```mermaid ` 格式

---

## 五、提示词模板（直接复制用）

### 5.1 创建笔记
```
帮我在 Obsidian 中创建一篇笔记，标题是"xxx"，存入 SQL笔记/07-日常工作总结，内容如下：
...
```

### 5.2 生成 ER 图
```
根据这段 SQL 生成 ER 图，连线标注 字段=字段 的格式：
[粘贴 SQL]
```

### 5.3 修改文件
```
帮我把 xxx 文件中的 xxx 修改为 xxx，保留我之前的个性化修改
```

### 5.4 执行命令
```
帮我运行 xxx 命令
```

---

## 六、使用原则总结

| 原则 | 说明 |
|------|------|
| ✅ **明确指定路径** | 告诉 AI 文件存在哪个目录 |
| ✅ **提供完整 SQL** | ER 图和探查结果更准确 |
| ✅ **标注个性化修改** | 在笔记中开辟记录区域，避免被覆盖 |
| ✅ **关闭 Accept 确认** | `continue.enableAcceptConfirmation = false` |
| ❌ **避免复杂内联代码** | 创建 `.py` 文件运行，不要在命令行写长脚本 |

---

> 最后更新: 2026-07-02
