# Anthropic Agent Design Principles

> 来源：Anthropic 官方工程博客 + Claude Code 团队实践，2024-2026

## 推荐模式谱系（从简到繁）

核心原则：**尽量简单，只在必要时加复杂度。**

### 基础：Augmented LLM
模型 + 检索 + 工具 + 记忆。做任何编排之前，先确认这个够不够。

### 六种编排模式

| 模式 | 做什么 | 什么时候用 |
|------|--------|-----------|
| Prompt Chaining | 顺序分解，步骤间程序化 gate check | 可以精确切分的任务，用延迟换准确率 |
| Routing | 分类输入 → 分发到专门 handler | 不同请求类型需要不同处理方式 |
| Parallelization | Sectioning（独立子任务并行）或 Voting（同任务多跑取最优） | 子任务无依赖，或需要 ensemble 决策 |
| Orchestrator-Workers | 中央 LLM 动态分解 → worker LLM 执行 → 合成 | 子任务无法预先指定，open-ended |
| Evaluator-Optimizer | 生成器 + 评估器 loop，直到达标 | 有清晰评估标准时 |
| Autonomous Agent | LLM 自主决定过程和工具使用，基于环境反馈 | 真正 open-ended 问题 |

模式可组合：routing + prompt chaining、orchestrator-workers + evaluator-optimizer。

## 好 Harness vs 坏 Harness

### 好 harness 的核心特征

1. **Progressive disclosure（渐进披露）** — SKILL.md 元数据先加载，完整内容按需获取。MCP 工具超过上下文 10% 自动切换搜索模式。Sub-agent 只回传 prompt + summary。Anthropic 实测将上下文从 77K 降到 8.7K，任务完成率从 49% 提到 74%。

2. **结构化跨 session 交接** — Feature list（初始全标记 failing）→ git 增量提交 → progress 文件 → init.sh。每次 session 读 log → 选一个 feature → 实现 → 提交 → 更新 progress → 停止。

3. **上下文是受限资源，不是无限假设** — Compaction 保连续但不解决"上下文焦虑"。结构化交接给 clean slate。Cache 优化 prompt 结构（缓存 token 成本只有基价的 10%）。

4. **工具策展是持续工程** — CC 有 ~20 个工具，团队持续追问每个是否还必要。重叠工具让 agent 困惑。模型变强后及时砍掉已死的 harness 组件。

5. **Sprint contract + 怀疑式评估** — 生成器和评估器在写代码前先谈判"什么是完成"。独立评估器（非自评）按具体标准打分，设硬阈值。

### 坏 harness 的共性
- 所有东西塞 system prompt，耗尽注意力预算
- 缺乏失败恢复机制
- 使用 Claude 不直观的过度专用工具
- 依赖自评（总是宽大）
- 编码了对模型能力已过时的假设

## 2026 年 SOTA 编排

- **5 层 Agent Stack:** MCP（连接）→ Skills（可复用专长）→ Agent SDK（执行 loop）→ Subagents（隔离并行 worker）→ Agent Teams（通信 worker，实验阶段）
- **Managed Agents**（2026.04）：Brain（Claude+harness）、Hands（sandbox/tools）、Session（append-only event log）三者解耦，各自可独立失败/替换
- **Hooks 扩展到 25+ 生命周期事件**，四种类型（command、HTTP、prompt、agent），每个生命周期点都能挂确定性 pre/post 动作
- **多 agent 架构兴起:** Planner → Generator → Evaluator 链，agent 间用文件通信而非共享上下文窗口

## 元原则

**Harness 工程是积累。** 每次 agent 犯错都变成一个 rule、hook 或 skill，永不再犯。harness 随时间变成制度性知识，让 agent 越来越可靠。
