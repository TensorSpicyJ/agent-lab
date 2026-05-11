# 物理 Agent Harness 架构设计

> 基于 ForgeCode、OpenCode、AITP v4.1 的架构分析，以及实际使用 AITP 进行量子混沌研究的 gap 发现
> 日期：2026-05-11

---

## 1. 问题诊断

### 1.1 当前 AITP 的三个核心缺陷

| 问题 | 表现 | 根因 |
|------|------|------|
| **不会"物理思考"** | AI 只会跑有 concrete benchmark 的任务，不会自发追问本质 | System prompt 缺乏引导物理推理的结构 |
| **工具调用太死** | skill 约束了工具但 AI 不知道什么时候该调哪个 | 缺少"场景→工具选择"的决策前置步骤 |
| **晋升 gate 模糊** | 不知道做到什么程度可以进入下一步 | Gate criteria 只有流程检查，没有"理解深度"引导 |

### 1.2 AITP v4.1 具体 Gap（2026-05-11 量子混沌 session 发现）

1. **自主自我怀疑能力缺失** — 没有机制让 AI 自主质疑 evidence 是否充分
2. **Retreat-and-return 缺失** — 回退到 L0/L1 后丢失 L3 精确位置
3. **Evidence 评分缺失** — 没有量化的 confidence scoring
4. **Cross-topic 知识复用缺失** — L2 查询是手动的，不会自动触发
5. **L3 subplane 状态持久化缺失** — 当前 subplane 不在 execution brief 中可视化

---

## 2. 架构设计

### 2.1 总览

```
┌──────────────────────────────────────────────────┐
│  LAYER 3: 轻量门控（3 个机械化 check）              │
│                                                   │
│  ① Promotion Gate: claim → ≥2 来源 + 理论/实验收敛  │
│  ② Contradiction Gate: 矛盾 → 裁决方案              │
│  ③ Publication Gate: claim-evidence map 完整性      │
│                                                   │
│  不检查"理解"，只检查"有还是没有"                    │
├──────────────────────────────────────────────────┤
│  LAYER 2: 物理思维引擎 ← 核心创新                    │
│                                                   │
│  注入到 Transform pipeline，每次 LLM 调用前强制：    │
│                                                   │
│  ① PHYSICAL ESSENCE                               │
│     "能标？对称性？自由度？该用什么框架？"             │
│                                                   │
│  ② KNOWLEDGE CONNECTION                           │
│     "L2 里有什么相关的？哪个假说跟这个有关？          │
│      已知极限能检验吗？"                             │
│                                                   │
│  ③ INFORMATION GAP                                │
│     "我缺什么信息？信源不足就 retreat                │
│      信 → 直接引用（标注 confidence）               │
│      不信 → 自己推导 → derivation-tracker           │
│      不确定 → 写 open question"                    │
│                                                   │
│  ④ GATE SELF-ASSESSMENT                           │
│     "做到什么程度算够？维度分析？极限检查？benchmark？ │
│     我能回答什么？"                                  │
│                                                   │
│  这不是 gate（gate 是外部机械化检查）                 │
│  这是 agent 在动手前的自我追问模板                    │
├──────────────────────────────────────────────────┤
│  LAYER 1: 工具 + 技能（场景驱动的工具选择）           │
│                                                   │
│  物理专用工具：                                      │
│  - derivation_tracker  (推导链管理)                 │
│  - dimension_analyzer  (量纲/能标分析)              │
│  - limit_checker       (已知极限化简验证)            │
│  - symmetry_analyzer   (对称性分析)                 │
│  - numerical_runner    (L4 数值执行，Fisher 远程)    │
│  - literature_search   (文献检索)                   │
│                                                   │
│  通用工具：read / write / shell / grep / web_search  │
│         task (子 agent 派发) / question (用户交互)   │
│                                                   │
│  工具选择不预声明 lane：                              │
│  Layer 2 物理思维阶段 agent 自己判断需要什么           │
├──────────────────────────────────────────────────┤
│  LAYER 0: 研究知识层（持久化大脑）                     │
│                                                   │
│  knowledge/lines/<line>/                           │
│    STATE.md          ← "现在知道什么"（agent 可读写）  │
│    hypotheses.md     ← 活跃假说 + evidence_type      │
│    open-questions.md ← 开放问题                      │
│    papers/           ← 论文结构化 insight            │
│    derivations/      ← 推导链                        │
│    experiments/      ← 实验记录                      │
│                                                   │
│  每条声明强制链回来源：[来源: DOI|等式编号, confidence] │
└──────────────────────────────────────────────────┘
```

### 2.2 核心设计决策

#### 决策 1：物理思维引擎是 prompt 模板，不是代码

从 ForgeCode 学到的最根本的事：agent 的行为 = model + system_prompt + tools。物理思维不需要新 MCP 工具，需要的是一个设计精良的 system prompt 模板。

实现方式：在 Agent 定义的 `custom_rules` 或 `system_prompt` 中嵌入 4 个强制追问，每次 LLM 调用前的 Transform pipeline 注入。

#### 决策 2：核心 loop 极简，Hook + Transform pipeline 扩展

借鉴 ForgeCode 的模式：
```
while !should_yield {
    → Fire Request hook
    → Transform pipeline (物理追问注入、知识层检索、工具排序)
    → LLM call
    → Fire Response hook (自我怀疑 hook)
    → Execute tools
    → Check gate conditions (机械化，非 LLM 自评)
    → Append results → continue or yield
}
```

新增 hook：
- `PhysicsSkepticHook`：每步后强制自我怀疑（evidence 够不够？要不要 retreat？）
- `RetreatTriggerHook`：自动检测 retreat 条件（source_coverage < 阈值？error bar 太宽？）
- `KnowledgeLookupHook`：每步前自动检索 L2 相关知识

#### 决策 3：Retreat checkpoint 借鉴 OpenCode 的 Part 级状态

不只是 "当前 L3"，而是精确到 subplane 级：
```
State checkpoint = {
  stage: "L3",
  subplane: "derive",
  activity: "verify_gauge_invariance",
  active_artifact: "derivations/gauge_invariance.md",
  partial_state: {
    last_step: 7,
    pending_checks: ["dimension_analysis", "known_limit_check"],
    confidence_scores: { source_coverage: 0.4, benchmark_coverage: 0.0 }
  }
}
```

Retreat 时保存 checkpoint，return 时精准恢复。

#### 决策 4：Gate 是机械化检查，永不用 LLM

从 Anthropic 指南 + 五源汇聚的核心共识：
```
Promotion Gate    = 文件存在？ frontmatter 完整？ ≥2 独立来源？
Contradiction Gate = 理论值和实验值都存在？ confidence 标注了？
Publication Gate   = claim-evidence map 每条 claim 有来源？ negative results 记录？
```

#### 决策 5：Agent 间用文件通信

L3（分析）↔ L4（数值执行）交互：
```
L3 写 task.md（算什么、参数范围、理论预期、成功标准）
    ↓ 文件传递
L4 (Fisher) 执行 → 写 results.md（数值 + 误差 + 收敛性）
    ↓ 文件传递
L3 读 results.md → 写 findings.md
```

#### 决策 6：成长机制 = 每次失败 → rule

```
Agent 推导错了
  → 分析根因（漏了极限检查？对称性分析不全？）
  → 写一条 rule："每次做微扰展开前必须先检查小参数是否存在"
  → rule 进入 AGENTS.md
  → 下次会话自动加载
  → 3 个月后 100 条 rules = 制度性物理知识
```

---

## 3. 与 AITP 的关系

AITP 的 L0→L1→L3→L4→L3→L2 流程**作为概念纲领保留**：

- 去掉 lane 前置锁定 — agent 自己判断需要什么工具
- 去掉 32 个 MCP 工具的操作负担 — 用精简的物理专用工具
- 保留 knowledge stage 概念 — L2 是"沉淀的正确知识"，晋升必须过 promotion gate
- 物理思维引擎是 L3 内部的 deliberation 引导，不是新 gate
- 把 AITP 的机械化 gate 提取为可复用的独立 harness 模块

---

## 4. 最小可行版本

```
1. 一个 LLM 调用（DeepSeek/Claude API）
2. 物理思维 system prompt（4 个追问模板）
3. 工具：read/write/shell/literature_search/grep
4. 一个 while loop（ForgeCode 风格的 orchestrator）
5. 一个 knowledge/ 目录（STATE.md + hypotheses.md）
6. 一个 promotion gate（机械化文件检查）
```

先在一条真实研究线（如 LSCO 假说验证或 toric code GSD=4）上裸跑，跑砸了就修 harness，循环迭代。

---

## 5. 实施路线

```
Phase 1  物理思维 system prompt 模板设计 + 测试
Phase 2  核心 loop（Forge-style orchestrator）+ 基本工具
Phase 3  Knowledge layer 接入（agent 启动时加载 STATE.md）
Phase 4  Retreat checkpoint 机制
Phase 5  Self-skeptic hook（每步后自动怀疑）
Phase 6  Evidence scoring（量化的 confidence 指标）
Phase 7  Promotion/Contradiction/Publication gates
```
