# Forge Agent Framework — 架构分析

> 来源：`D:\Playground\omw-windows-build\oh-my-warp\vendor\forge-code\`，Rust 实现，19 crates

## Crate 四层架构

```
Domain Layer (forge_domain)     ← 纯类型 + trait，无依赖
    ↓
Service Layer (forge_services)  ← 实现 domain trait
    ↓
Application Layer (forge_app)   ← 编排：agent loop、hook、工具派发
    ↓
Infrastructure Layer             ← 具体实现：文件 I/O、进程执行、embedding
```

**核心原则：** trait-based DI，每个 service 接收 `Arc<F>` 组合 trait bound，service 间无直接依赖。这是 Forge 自己的 `AGENTS.md` 里写明的模式。

## Agent Loop（`Orchestrator::run`）

`while !should_yield` 状态机，每轮：

```
1. [Session Start]   Fire Start hook
2. [Context Sync]    保存对话到 store
3. [Request Hook]    Fire Request hook
4. [Transform Pipe]  SortTools → NormalizeArgs → ImageHandling → DropReasoning → ...
5. [LLM Call]        execute_chat_turn() → stream content deltas
6. [Response Hook]   Fire Response hook
7. [Term Check]      finish_reason=Stop && 无 tool_calls → yield
8. [Tool Execute]    Task 工具并行（join_all），其余顺序
9. [Error Track]     每工具失败计数，达阈值后注入 retry message
10.[Context Append]  追加 assistant message + tool results
11.[End Hook]        若 yield，Fire End hook；若 End hook 添加了新消息，**重新进入 loop**
12.[TaskComplete]    信号 UI
```

### 关键设计
- **Yield 条件**：finish_reason=Stop 且无 tool calls，或 Followup 工具请求用户输入
- **End hook 重入**：compaction 等 End hook 若追加了新消息到对话，loop **不退出而是继续**
- **Transform pipeline**：每次 LLM 调用前，一条 transformer 链独立处理排序/规范化/推理/图片，与核心 loop 解耦

## 工具系统

### ToolCatalog
17 个工具变体的 enum，自动派生 JSON Schema + `ToolDescription`（从 `src/tools/descriptions/*.md` 加载）：

```
Read | Write | FsSearch | SemSearch | Remove | Patch | MultiPatch |
Undo | Shell | Fetch | Followup | Plan | Skill | TodoWrite | TodoRead | Task
```

- Schema 在解析时用 `forge_json_repair::coerce_to_schema` 强制修正 LLM 输出
- ToolDescription 是 Handlebars 模板，按当前模型能力动态渲染（如模型不支持 image，Read 工具描述就去掉图片相关段）

### 三级派发（ToolRegistry::call_inner）
1. 查 ToolCatalog → 解析+派发
2. 查已注册 sub-agent（AgentExecutor）→ 匹配则委托
3. 查 MCP 工具（McpExecutor）→ 匹配则委托

### 权限检查
受限模式下，`check_tool_permission()` 把工具输入映射为 PermissionOperation（Read/Write/Execute/Fetch）→ PolicyEngine 判决：
- Allow → 直接执行
- Deny → 阻止
- Confirm → 弹窗让用户 Accept/Reject/AcceptAndRemember（记住的生成新 policy rule 持久化）

## Skill 系统

### 格式
```markdown
---
name: skill-name
description: What & when to use. PRIMARY trigger.
---
# Skill Title
正文只在触发后加载。
```

### 渐进披露（三级加载）
1. **元数据**（name+description）始终在上下文（~100 words）
2. **正文**触发时加载（目标 <5K words）
3. **Bundled resources**按需加载

### 加载优先级
CWD `.forge/skills/` > Agents `~/.agents/skills/` > Global `~/forge/skills/` > Built-in（二进制内嵌）

冲突处理：保留最后出现的。

### 内置技能（3 个）
- `create-skill` → 脚手架新技能
- `execute-plan` → 执行结构化 plan 文件（`[ ]`/`[~]`/`[x]`/`[!]` 状态标记）
- `github-pr-description` → 从 git diff 生成 PR 描述

## Hook 系统

6 个生命周期事件，每个事件有类型化的 EventHandle trait：

| 事件 | 触发点 | Payload |
|------|--------|---------|
| Start | 对话处理开始 | 空 |
| End | 处理结束 | 空（可追加消息到对话，触发重入） |
| Request | 每次 LLM 调用前 | request_count |
| Response | 每次 LLM 响应后 | 完整 message |
| ToolcallStart | 工具执行前 | tool call |
| ToolcallEnd | 工具执行后 | call + result |

Handler 通过 `.zip()` 和 `.and()` 组合。内置处理：
- Compaction（压缩检测）
- DoomLoopDetector（死循环检测）
- PendingTodosHandler（未完成任务提醒）
- TitleGeneration（会话标题生成）
- Tracing（调试追踪）

自定义 handler 可通过闭包挂载，无需实现 trait。

## 值得借鉴的 7 个模式

1. **Enum-based tool catalog + proc macros。** 工具是 enum 变体，JSON Schema 自动派生，描述从外部 .md 加载。声明式、自文档化。

2. **Transform pipeline。** 交叉关注点（排序、规范化、推理处理、图片处理）从核心 loop 解耦为 transformer 链。

3. **Hook 组合。** `.zip()` 和 `.and()` 让 hook 像 middleware 一样可组合，无需改动核心 loop。

4. **Tool description 模板化。** 根据模型能力动态渲染工具描述——支持 image 的模型看到的 Read 描述和不支持的模型不同。

5. **Schema 强制修正。** `forge_json_repair` 在解析 LLM JSON 参数前先对 schema 做修正（如 string→int 转换），容忍常见 LLM 输出错误。

6. **子 agent 工具白名单。** 每个 agent 有自己的 `tools: Vec<ToolName>`，支持 glob pattern（`mcp_*`）。agent 只能用它被允许的工具。

7. **Session 复用。** 子 agent 通过 `session_id` 实现对话复用，不是每次都从零开始。
