# 交叉模式综合

> 对比五条线：Anthropic 官方指南、superpowers 技能系统、AITP 协议、Claude Code 泄露源码、Forge 框架

## 五源概览

| 来源 | 性质 | 语言 | 核心贡献 |
|------|------|------|----------|
| Anthropic 官方 | 工程博客+指南 | 英文 | 6 模式谱系、好/坏 harness 判断标准、context engineering |
| Superpowers | 插件技能系统 | Markdown | Iron Law、理性化防御、Plan 格式、sub-agent 审查循环 |
| AITP | 研究协议 | Python+Markdown | 六阶段门控、机械化 gate 评估、知识权威层级、L4→L3 强制回环 |
| CC 泄露 | 工程源码 | TypeScript | 12 层包装器、40+ 工具生命周期、六层权限防御、Coordinator 无工具访问权 |
| Forge | 开源框架 | Rust | 四层 clean architecture、Transform pipeline、Hook 组合、Tool 模板化描述 |

## 共现模式（四条以上线都出现的）

### 1. 门控是 harness 的第一功能
| 来源 | 实现 |
|------|------|
| Anthropic | Prompt chaining 的 programmatic gate checks |
| Superpowers | Iron Law + verification gates、spec review 必须先于 code review |
| AITP | 机械化 gate 评估（检查文件存在/字段/标题）+ 过渡限制 |
| CC 泄露 | 工具独立 `validateInput()` + `checkPermissions()` + 六层权限防御 |
| Forge | PolicyEngine 三态判决（Allow/Deny/Confirm） |

**共同观点：** agent 的"我完成了"永远不能信任。门控必须是程序化/机械化验证。

### 2. 上下文作为受限资源
| 来源 | 实现 |
|------|------|
| Anthropic | Progressive disclosure、MCP >10% auto-search、cache optimization |
| Superpowers | Fresh context per agent、子 agent 绝不继承父上下文 |
| AITP | SessionStart hook 按 stage 注入技能、按需加载不预装全部 |
| CC 泄露 | 9 段结构化 compaction + 三层记忆架构 |
| Forge | Skill 三级渐进披露（元数据→正文→资源）+ 动态模板化工具描述 |

**共同观点：** 上下文 = 金钱+延迟+质量。精确管理谁看到什么、什么时候看到。

### 3. Agent 间用文件通信，不用共享上下文
| 来源 | 实现 |
|------|------|
| Anthropic | "shift worker" 模式：读 log → 选 feature → 提交 → 更新 progress → 停止 |
| Superpowers | Plan 文件承载 state、Git commit 为 checkpoint |
| AITP | Markdown+frontmatter 即状态数据库，可 diff/grep/版本控制 |
| CC 泄露 | Structured XML `<task-notification>` 回传、Coordinator 只路由不执行 |
| Forge | Sub-agent session 复用，结果通过 `ToolOutput` 结构化回传 |

**共同观点：** 窗口不共享，接口要结构化。

### 4. Hook/生命周期是扩展点，不是后加功能
| 来源 | 实现 |
|------|------|
| Anthropic | 25+ 生命周期事件、四种 hook 类型 |
| Superpowers | REQUIRED SUB-SKILL 标记定义依赖图 |
| AITP | SessionStart hook 评估 gate → 注入技能 |
| CC 泄露 | 12 层渐进包装器堆叠在核心 loop 上（工具调度→规划→子 agent→技能→压缩→持久→后台→团队→协议→自主→隔离） |
| Forge | 6 事件 hook 系统 + `.zip()` `.and()` 组合 + End hook 可重入 loop |

**共同观点：** hook 不是 feature，是架构。核心 loop 极简（`while true`），所有扩展通过 hook/wrapper 层完成。

## 各线的独有贡献

### Superpowers — agent 心理学
理性化防御表（Excuse→Reality 两列）、Red Flags: STOP 列表、沉没成本显式提醒。**五条线中唯一系统化研究"agent 如何欺骗自己"的。**

### AITP — 知识状态模型
按阶段的知识权威层级 + lane-specific evidence requirements。**五条线中唯一形式化了"这个 claim 凭什么可信"。**

### Anthropic — 工程经济学
成本感知模型选择、缓存优化、工具策展运维。"什么时候用便宜模型"是工程决策，不是研究问题。

### CC 泄露 — 安全深度
六层权限防御、cch 加密认证、Coordinator 被剥夺工具访问权。"只协调不执行"的安全边界设计精妙。**反蒸馏机制**提示了商业化 AI 产品需要防御竞争对手的模型提取。

### Forge — 架构清洁度
19 crate 四层分离、trait-based DI、enum 工具 catalog + proc macro 代码生成。最干净的开源实现参考。

## 更新的实验方向

1. **可复用的机械化 gate 组件** — 从 AITP 提取：检查文件存在、frontmatter 字段、正文标题。做成独立 harness 模块。
2. **Transform pipeline** — 从 Forge 提取：每次 LLM 调用前的 transformer 链（排序→规范化→推理处理→模型特定适配）。这是交叉关注点解耦的标准模式。
3. **Hook 组合语义** — 从 Forge+CC 提取：`.zip()` `.and()` 组合 + End hook 重入 loop。定义 hook 的最小接口。
4. **Coordinator 无工具模式** — 从 CC 泄露提取：上层协调器被剥夺直接文件访问权，只能路由消息和派发 worker。这是多 agent 安全边界的核心 insight。
5. **反蒸馏/安全防御** — 从 CC 泄露提取：注入假工具定义污染蒸馏训练数据。agent 时代的安全不仅是权限，还包括知识产权防御。

---

## 2026-05-11 更新：ForgeCode vs OpenCode 深度对比后的新洞察

### 第六源：OpenCode

| 来源 | 性质 | 语言 | 核心贡献 |
|------|------|------|----------|
| OpenCode | 开源 agent 框架 | TypeScript (Bun + Effect-TS) | Part 级 session 持久化、Stream 事件驱动 loop、Effect-TS DI、ACP 标准化协议 |

### 新增共现模式

#### 6. Agent 定义 = 纯数据，不是代码

| 来源 | 实现 |
|------|------|
| Forge | `Agent { id, tools, model, system_prompt, custom_rules }` — 填 struct 即创建 agent |
| OpenCode | `Agent.Info { name, mode, permission, prompt, steps }` — Schema 定义即创建 agent |
| CC 泄露 | Agent 配置文件定义 coordinator/worker 角色 |
| Anthropic | Managed Agents：Brain + Hands + Session 三者解耦 |

**共同观点：agent 行为 = model × system_prompt × tools。新 agent = 新配置，不写代码。**

#### 7. Session 持久化粒度决定 agent 可恢复性

| 来源 | 粒度 |
|------|------|
| OpenCode | Part 级（text/tool/reasoning/step-start/step-finish/patch 独立行） |
| Forge | Message 级（Conversation 整体保存） |
| AITP | File 级（state.md 文件即状态） |
| CC 泄露 | Memory 三层架构（文件/grep/Kairos 守护进程） |

**关键洞察：OpenCode 的 Part 级粒度是 retreat checkpoint 的最佳参考。** 不是 "当前在 L3"，而是精确到 subplane + activity + partial_state。每次 retreat 保存完整 snapshot，return 时精准恢复。

### 新增实验方向

6. **物理思维引擎（Physics Thinking Injection）** — 从 Forge 的 Transform pipeline 借鉴：每次 LLM 调用前，transformer 注入 4 个强制追问（物理本质/知识关联/信息缺口/完成标准）。不是新 gate，是 agent 内部的 deliberation 引导模板。

7. **Retreat checkpoint 机制** — 从 OpenCode 的 Part 级状态 + AITP 的 retreat 工具借鉴：保存 `{stage, subplane, activity, active_artifact, partial_state}` 五元组，return 时精准恢复，不丢失 L3 推导位置。

8. **Self-skeptic hook** — 从 superpowers 的"agent 心理学" + AITP 的 physicist-check 借鉴：每步推导后自动触发证据审计（source coverage / benchmark coverage / error bar tightness），低于阈值自动建议 retreat。

9. **知识层双向索引** — 从 agent-lab 的 knowledge layer 设计 + Forge 的 sem_search/grep 双层检索借鉴：INDEX.md 全局概念索引（grep 毫秒级），embedding 语义搜索（秒级 fallback）。每次 L3 新步骤前、新假说创建时、claim promote 前自动触发 L2 检索。
