# 自主研究 Agent 设计方案

> 写给合作者看的完整设计文档。覆盖：要解决什么问题、设计哲学、架构、关键决策、当前进展。

---

## 1. 要解决什么问题

**目标**：构建一个适合凝聚态物理研究工作流的通用自主研究 agent。不是某个课题的专用工具，而是长期可演进的科研 agent 基础设施。

**当前痛点**：
- agent 每次会话启动时"脑子一片空白"，不知道研究线读过什么论文、有什么活跃假说、开放问题在哪里
- 已有的 AITP 协议（6 层门控、32 个 MCP 工具、367 个测试）建了精密审批流程，但 agent 没有持久化的领域知识时门控只是在真空里做质量管控
- 理论推导和实验数据分散在不同仓库里，agent 无法交叉验证

**核心主张**：先建 agent 的脑（知识层），再装眼和手（技能），最后在关键路口放哨（轻量门控）。顺序不能反。

---

## 2. 设计哲学

### 2.1 四套系统的教训

| 系统 | 借鉴了什么 | 避免了什么 |
|------|----------|----------|
| **AITP**（自有，v1.0→v2.9） | 文件即状态、topic 目录结构、contracts 模板设计 | 全流程门控、线性流水线、32 工具的操作负担、lane 前置锁定 |
| **Feynman agent**（getcompanion-ai） | Source grounding（每条声明链回原始来源）、skill 文件驱动 agent 行为 | CLI 专属形态（我们要的是一套可嵌入现有 agent 的知识+skill 体系） |
| **ChemGraph**（Argonne, 2026） | Executor 上下文隔离、Planner→Executor→Aggregator 三层拆分、基准测试方法论 | 无跨任务知识持久化（我们的 research-knowledge 层正好补这个） |
| **Stanford Virtual Lab**（Nature 2025） | PI agent + 专精 agent + Scientific Critic 的多角色协作 | 单一领域的端到端自动化（我们要的是多研究线通用框架） |

### 2.2 核心原则

1. **知识层是起点不是终点** — agent 启动时加载研究状态，不是做完研究才写入
2. **理论实验不拆分** — 同一条线内推导和实验数据共存，通过 `evidence_type` 标注区分但不隔离存储
3. **不预声明 lane/mode** — agent 根据 STATE.md 的实际内容自然判断需要什么 skill，不做前置分类
4. **Source grounding 铁律** — 每条声明必须链回原始来源（DOI、样品ID、等式编号）
5. **文件即状态** — 纯 Markdown，不引入数据库，Claude Code 可直接读写
6. **Skill 跟着真实用例长** — 不预先设计，等真的有推导链了再写 derivation-tracker
7. **上下文隔离** — 每个 skill 只加载完成任务所需的最小上下文，不随手全量加载

---

## 3. 三层架构

```
┌──────────────────────────────────────────────┐
│            LIGHT GATES (轻量门控)              │
│    只在 promotion / contradiction 介入        │
├──────────────────────────────────────────────┤
│          CAPABILITY SKILLS (按需激活)          │
│                                              │
│  通用: paper-to-insight | state-overview     │
│        hypothesis-tracker                    │
│  实验向: experiment-analyzer                  │
│  理论向: derivation-tracker                   │
│  交叉: theory-vs-experiment                  │
├──────────────────────────────────────────────┤
│       RESEARCH KNOWLEDGE LAYER (统一知识脑)    │
│                                              │
│  研究线 STATE | 论文 insight | 开放问题 |       │
│  假说跟踪(evidence_type标注) | 跨线关联         │
│  实验记录 | 推导链 | 方法积累                   │
└──────────────────────────────────────────────┘
```

### 3.1 Layer 1: 研究知识层

agent 的持久化记忆。按研究线组织，每条线有 `STATE.md + hypotheses.md + open-questions.md` 三件套。理论和实验内容共存于同一研究线下。

目录结构：
```
research-knowledge/
├── INDEX.md                      # 全局索引
├── lines/
│   ├── lsco-single-layer/        # 偏实验线（但也可有 derivations/）
│   │   ├── STATE.md              # 认知状态 — agent 可读写
│   │   ├── hypotheses.md         # 活跃假说，标注 evidence_type
│   │   ├── open-questions.md     # 开放问题，按优先级
│   │   ├── papers/               # 论文结构化 insight
│   │   ├── experiments/          # 实验记录（实验线才有）
│   │   └── derivations/          # 推导链（理论线才有）
│   ├── superconducting-diode/    # 混合线
│   ├── sc-magnetic/              # 混合线
│   └── topological-order/        # 纯理论线（无 experiments/）
├── cross-cutting/
│   ├── connections.md            # 跨线关联
│   └── theory-experiment/        # 理论↔实验交叉验证记录
└── methodology/
    ├── experimental/             # MBE 食谱、XRD 参数、工具注册表
    └── theoretical/              # 常用推导框架、符号约定
```

关键设计：
- **STATE.md 关注"现在知道什么"**，分"来自实验"和"来自理论/推导"两个区块，每条事实有来源和 confidence
- **假说标注 evidence_type**（theoretical / experimental / mixed），影响后续 skill 的激活逻辑和 promotion gate 的检查标准
- **agent 可以写 STATE.md** —— 读完论文发现新事实？直接更新。实验结果返回？直接更新
- **source grounding** 贯穿所有文件：每条声明后跟 `[来源: <DOI|样品ID|等式编号>, confidence: high|medium|low]`

### 3.2 Layer 2: 能力技能

基于 superpowers skill 格式，每个 skill 是一个 Markdown 文件，定义触发条件、工作流和上下文预算。

**通用 Skills：**

| Skill | 功能 | 上下文预算 |
|-------|------|----------|
| `state-overview` | agent 启动时加载研究状态，输出结构化概览 | INDEX + STATE.md + hypotheses(仅标题) + open-questions(仅高优) |
| `paper-to-insight` | 读论文→提取结构化 insight→更新知识层 | 目标论文 + STATE.md(假说摘要) + hypotheses.md(相关假说) |
| `hypothesis-tracker` | 创建/更新假说条目，关联证据，标记状态 | 当前线 hypotheses.md + STATE.md |

**实验/理论向 Skills（按需激活，等真实用例驱动）：**

| Skill | 触发条件 |
|-------|---------|
| `experiment-analyzer` | 新 XRD/输运/RHEED 数据到达 |
| `derivation-tracker` | 新推导步骤 / 理论论文 / 推导链缺口 |
| `theory-vs-experiment` | 同一条假说同时有理论预测和实验数据 |

**激活逻辑**（agent 内部判断，无需人工切换）：
```
agent 启动 → state-overview 加载 STATE.md
         → 读到 hypotheses.md，发现有"待验证"假说
         → evidence_type 含 experimental → 有新数据？ → experiment-analyzer
         → evidence_type 含 theoretical → 推导链有缺口？ → derivation-tracker
         → 同时有理论预测和实验数据 → theory-vs-experiment
```

**上下文隔离规则**（来自 ChemGraph 分析）：
- 每个 skill 文件开头声明 `## Context Budget`：必须加载和禁止加载的文件列表
- 违反 context budget 的调用视为不合格
- 原则：只加载完成任务所需的最小上下文，不随手全量加载

### 3.3 Layer 3: 轻量门控

**只在三个关键节点介入**，不像 AITP 那样每一步都拦截：

**Gate 1: Promotion Gate**
- 触发：假说从 "active" → "established"
- 检查：≥2 个独立来源支持？mixed 假说的理论+实验是否收敛？有无未解释的 contradictory evidence？
- 操作：人审批后写入 STATE.md 的 established 区

**Gate 2: Contradiction Gate**
- 触发：理论预测和实验数据矛盾，或两条独立实验矛盾
- 检查：矛盾是真实的还是表面的？哪端 confidence 更高？
- 输出：裁决方案（新实验 / 更精确推导 / 暂时搁置）

**Gate 3: Publication Gate**
- 触发：研究线达到可发表状态
- 检查：claim-evidence map 完整？每条 claim 有来源？negative results 如实记录？
- 输出：论文草稿骨架 + 证据追溯表

---

## 4. 关键设计决策

### 4.1 为什么理论实验不拆分

AITP 的做法是用 `lane`（formal_theory / toy_numeric / code_method）前置声明研究类型，agent 被 lane 锁定。我们的研究线本身就是理论实验混合的（比如 LSCO 线既有 Makarov 的理论又有自有 XRD 实验），拆成两个系统等于把同一条线的认知切成两半。

我们的做法：不声明 lane，研究线的实际目录结构（有没有 `experiments/` 和 `derivations/`）自然决定 skill 激活范围。evidence_type 标注在假说级别而非研究线级别，agent 根据假说的实际需求激活对应 skill。

### 4.2 为什么不先建全部门控

AITP 的经验：门控先建 = 质量管控在真空里运行。agent 没有持久化知识时，每个 gate 检查的是"流程是否走完"而非"研究是否有内容"。我们的顺序是：先让 agent 能看懂研究状态 → 先让 agent 能产出结构化 insight → 再在真正需要人审的节点加 gate。

### 4.3 为什么用文件而非数据库

- Claude Code 天然读写 Markdown，不需要 MCP 工具中转
- Git diff 就是变更记录
- 人可以随时打开看和改
- 不引入新的依赖

### 4.4 为什么 Skill 等真实用例驱动

derivation-tracker 的模板可以 30 分钟写完，但如果 `derivations/` 目录是空的就没有东西可以 track。跟着真实用例长出来的 skill，第一次跑通就是已验证的。

---

## 5. 当前进展（2026-05-08）

**已建成：**
- 4 条研究线的统一知识层（16 个 Markdown 文件）
  - LSCO 单层：4 个活跃假说、7 个开放问题、7 篇论文 insight（已填充）
  - 超导二极管、超导磁性材料：种子期骨架
  - 拓扑序：已建立（toric code GSD=4 已证明）
- `paper-to-insight` skill — 论文→结构化 insight 的完整工作流
- `state-overview` skill — agent 启动时的研究状态加载流程
- `CLAUDE.md` §0 — agent 在研究任务时自动加载知识层的指令
- 工具注册表（`methodology/experimental/tool-registry.md`）
- 跨线关联文档（3 个交叉议题）

**设计好但未建（等真实用例）：**
- derivation-tracker、theory-vs-experiment、experiment-analyzer skills
- 3 个 light gates
- 基准测试套件（`.benchmarks/`，等 skill ≥ 4 且论文 ≥ 20 篇时建立）

---

## 6. 实施路线图

```
Phase 1 ✓  知识层骨架 + STATE.md 填充 + 论文迁移
Phase 2 ✓  paper-to-insight skill + state-overview skill
Phase 3    第一条假说推至可验证（如 LSCO H1: c轴 vs Tc correlation）
Phase 4    写 derivation-tracker（当第一条推导链产生时）
Phase 5    写 theory-vs-experiment（当第一条理论预言和实验数据同时存在时）
Phase 6    加 Promotion Gate（当第一条假说准备 promoted to established 时）
Phase 7    建立基准测试套件
```

---

## 7. 文件索引

| 文件 | 用途 |
|------|------|
| `D:\Playground\research-knowledge\INDEX.md` | 全局研究线总览 |
| `D:\Playground\research-knowledge\lines\<line>\STATE.md` | 研究线认知状态 |
| `D:\Playground\research-knowledge\lines\<line>\hypotheses.md` | 假说跟踪 |
| `D:\Playground\research-knowledge\lines\<line>\open-questions.md` | 开放问题 |
| `D:\Playground\research-knowledge\lines\<line>\papers\<slug>.md` | 论文结构化 insight |
| `D:\Playground\research-knowledge\cross-cutting\connections.md` | 跨线关联 |
| `D:\Playground\research-knowledge\methodology\experimental\tool-registry.md` | 实验工具注册表 |
| `D:\Playground\skills\research\paper-to-insight\SKILL.md` | 论文→insight skill |
| `D:\Playground\skills\research\state-overview\SKILL.md` | 状态加载 skill |
| `D:\Playground\CLAUDE.md` | agent 启动入口（§0 为知识层加载指令） |
| `D:\Playground\docs\research-agent-design.md` | 本设计文档 |
| `C:\Users\TaiS\.claude\plans\lazy-gathering-puffin.md` | 实施计划（含 ChemGraph 分析） |
