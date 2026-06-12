# AITP vs 科学领域 RAG/KG 结构对比分析

> 对比对象：GitHub/bhjia-phys/AITP-Research-Protocol (v5 typed kernel)
> 对比基准：MIT SCIGRAPHRAG / Knowledge Graph RAG / CMT50 知识卡片
> 2026-06-06

---

## 一、AITP 是什么？—— 核心定位

AITP (AI-assisted Theoretical Physics Research Protocol) 不是传统意义上的"知识库"或"检索系统"。它是一个**研究过程协议层**，包裹在 Agent 外部，强制将研究活动写入 typed、可 replay 的记录。

### 1.1 AITP v5 的核心记录类型

```
┌─────────────────────────────────────────────────────────────┐
│  AITP v5 Typed Kernel Records                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  组织层：                                                    │
│    - topic          研究主题（如 "FQHE"）                   │
│    - session        研究会话                                │
│    - claim          当前活跃的科学主张                       │
│                                                             │
│  内容层：                                                    │
│    - definitions    定义                                      │
│    - physics objects    物理对象                             │
│    - object relations   对象关系                             │
│    - assumptions    假设                                    │
│                                                             │
│  证据层：                                                    │
│    - evidence       证据记录                                │
│    - code state     代码状态溯源                            │
│    - tool recipes/runs  工具配方/运行记录                    │
│    - references     参考文献位置                            │
│                                                             │
│  验证层：                                                    │
│    - validation contracts   验证合约                        │
│    - validation results     验证结果                        │
│    - human checkpoints      人工检查点                        │
│                                                             │
│  信任层：                                                    │
│    - failure-mode review packets  失败模式审查                 │
│    - promotion packets          晋升包（进入 L2 memory）       │
│    - trust audits               信任审计                      │
│    - L2 memory entries          长期记忆条目                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 AITP 的核心哲学

| 直接 Agent 聊天 | AITP 协议层 |
|----------------|------------|
| 对话历史是主要记忆 | Typed records 是持久记忆 |
| Agent 可能混淆 claim、evidence、summary | Claim、evidence、validation、uncertainty 是分离记录 |
| "看起来对" 可能成为粘性错误 | 信任变更需要 validation 和 checkpoints |
| 后续会话依赖回忆 | 后续会话从 execution briefs 和 replay packets 恢复 |
| 长期笔记可能漂移 | L2 memory 保持 provenance、scope、validation links、failure modes |

**关键洞察**：AITP 记录的是**研究过程**（process），不是**领域知识**（content）。

---

## 二、两种知识图谱的本质区别

### 2.1 领域知识图谱（Domain KG）—— 之前讨论的方向

```
┌─────────────────────────────────────────────────────────────┐
│  领域知识图谱（如 SCIGRAPHRAG / CMT50 知识卡片）              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  节点类型：                                                  │
│    - Method: VMC, DMRG, DQMC, ED, PEPS                     │
│    - Observable: ground_state_energy, spin_correlation       │
│    - Model: Hubbard_model, Heisenberg_model                 │
│    - Uncertainty: sign_problem, truncation_error           │
│    - StandardResult: exact_solution, scaling_law           │
│                                                             │
│  关系类型：                                                  │
│    - (Method) --[estimates]--> (Observable)                 │
│    - (Method) --[suffers_from]--> (Uncertainty)             │
│    - (Model) --[solved_by]--> (Method)                    │
│    - (Model) --[has_exact_solution]--> (StandardResult)    │
│                                                             │
│  用途：回答"这个物理问题怎么解？"                            │
│  构建方式：从论文/教科书提取，预构建                         │
│  生命周期：静态（季度/月度更新）                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 研究过程图谱（Research Process Graph）—— AITP 的方向

```
┌─────────────────────────────────────────────────────────────┐
│  研究过程图谱（AITP v5）                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  节点类型：                                                  │
│    - Claim: "Finite-size counting identifies edge sector"   │
│    - Evidence: 数值计算结果、符号推导、文献引用              │
│    - Validation: 验证合约 + 验证结果                         │
│    - PhysicsObject: 研究中定义的数学对象（如 "sigma-z OTOC"）│
│    - ToolRun: 某次 Python/SymPy 执行记录                     │
│                                                             │
│  关系类型：                                                  │
│    - (Claim) --[supported_by]--> (Evidence)               │
│    - (Evidence) --[derived_from]--> (ToolRun)               │
│    - (Claim) --[has_failure_mode]--> (FailureMode)        │
│    - (Claim) --[promoted_to]--> (L2Memory)                │
│    - (L2Memory) --[scope]--> (Topic)                      │
│                                                             │
│  用途：回答"这个研究进行到哪了？哪些可信？"                  │
│  构建方式：研究过程中实时写入                                │
│  生命周期：动态（随研究进展更新）                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 本质区别对比

| 维度 | 领域知识图谱（Domain KG） | 研究过程图谱（AITP） |
|------|--------------------------|---------------------|
| **记录什么** | 物理世界的知识（方法、模型、结果） | 研究活动的轨迹（主张、证据、验证） |
| **谁构建** | 知识工程师 / LLM 从文献提取 | 研究 Agent 在运行时写入 |
| **何时构建** | 预构建（离线） | 实时构建（在线） |
| **查询什么** | "VMC 怎么估计能量？" | "我上次验证到哪了？" |
| **信任机制** | 无（知识本身不标记可信度） | 强（validation gates trust） |
| **错误处理** | 无（知识不标记错误模式） | 强（failure-mode review packets） |
| **适用范围** | 通用物理问题 | 特定研究项目 |
| **与 LLM 关系** | LLM 是**消费者**（检索知识） | LLM 是**生产者**（写入记录） |

---

## 三、对 CMT50 场景的具体对比

### 3.1 如果用"领域知识图谱"解 CMT50

```
用户问："Hubbard 模型 N=4, U=2 的基态能量是多少？"

检索过程：
  1. 查询 (Hubbard_model) --[ground_state]--> (energy)
  2. 找到 (Hubbard_model) --[solved_by]--> (ED)
  3. 检索 ED 在 N=4, U=2 下的标准结果
  4. 返回：E_0 = -2.0t (假设)

Agent 行为：
  - 得到知识 → 理解原理 → 应用到题目 → 给出答案
  - 可能调用 symbolic_verifier 验证

优势：
  - 有预置知识，不需要从零推导
  - 跨文档关联，避免碎片化

劣势：
  - 如果题目是变体（N=6），预置知识可能不足
  - 如果知识库中没有该具体参数的结果，无法回答
```

### 3.2 如果用"AITP 研究过程"解 CMT50

```
用户问："Hubbard 模型 N=4, U=2 的基态能量是多少？"

AITP 工作流：
  1. 创建 topic: "hubbard_n4_u2"
  2. 创建 claim: "基态能量是 X"
  3. 创建 evidence: 需要数值或符号证据
  4. 创建 validation contract: "使用 ED 对角化验证"
  5. Agent 调用 code_runner 执行 Python/NumPy 对角化
  6. 记录 tool run: 代码、输入、输出
  7. 记录 validation result: 通过/失败
  8. 如果通过，创建 promotion packet 进入 L2 memory
  9. 返回答案 + 完整研究轨迹

Agent 行为：
  - 不依赖预置知识，而是实时计算/推导
  - 每一步都有记录、验证、溯源

优势：
  - 对任意参数（N=4, N=6, U=2, U=4）都能处理
  - 结果可信度高（有 validation 和 tool run 支撑）
  - 错误可追溯（知道哪一步出错了）

劣势：
  - 需要更多时间（实时计算而非检索）
  - 对概念性题目（如"哪个估计量无偏？"）帮助有限
```

### 3.3 关键洞察：两者是互补的，不是替代的

| CMT50 题目类型 | 领域 KG 的作用 | AITP 的作用 | 最佳组合 |
|---------------|--------------|------------|----------|
| 概念性选择题（"哪个方法无偏？"） | ✅ 提供知识支撑 | ⚠️ 有限（需要预置知识） | 领域 KG 检索 + AITP 记录 claim/evidence |
| 数值计算题（"N=4 的基态能量"） | ⚠️ 可能无预置结果 | ✅ 实时计算 + 验证 | AITP 主导，领域 KG 提供方法选择 |
| 符号推导题（"推导 O_n 的表达式"） | ⚠️ 可能无直接公式 | ✅ 符号计算 + 验证 | AITP 主导，领域 KG 提供相关公式参考 |
| 比较题（"DMRG vs ED 的精度"） | ✅ 提供方法特性 | ✅ 记录比较过程 | 两者结合 |
| 研究级难题（CMT50 大部分题目） | ⚠️ 知识库可能覆盖不足 | ✅ 强制验证和推理 | AITP 主导，领域 KG 辅助 |

---

## 四、AITP 对 Hakimi 的启示

### 4.1 AITP 解决了 Hakimi 的什么问题？

回顾 Hakimi CMT50 的实验结果：

| 问题 | Hakimi 现状 | AITP 的解决方案 |
|------|------------|----------------|
| Agent 给出答案但无法解释为什么 | 无推导审计 | AITP 的 claim/evidence/validation 分离 |
| 答案错误但不知道错在哪 | 错误归因靠人工 | AITP 的 failure-mode review packets |
| 同一题目多次运行结果不同 | 无版本控制 | AITP 的 session/topic 恢复机制 |
| Agent "看起来对" 的答案被信任 | 无信任门槛 | AITP 的 validation gates trust |
| 长推理链超时后无中间状态 | 超时 = 完全丢失 | AITP 的 tool run 记录（即使超时也有部分记录） |
| 无法区分"检索猜测"和"蒸馏理解" | 无验证机制 | AITP 的 validation contracts |

### 4.2 AITP 的"验证合约"设计对 CMT50 的启发

AITP 的 validation contract 是一个关键创新：

```yaml
validation_contract:
  claim: "VMC 梯度估计量是无偏的"
  validation_method: "symbolic_derivation"
  required_evidence:
    - type: "formula_derivation"
      must_show: "E[∂E/∂α] = ∂E/∂α"
    - type: "limit_check"
      must_show: "N→∞ 时偏差 → 0"
  failure_modes:
    - "近似波函数引入偏差"
    - "有限样本引入方差（非偏差）"
  promotion_criteria:
    - "所有 required_evidence 通过"
    - "无未解决的 failure modes"
    - "人工 checkpoint 通过"
```

**应用到 CMT50**：

对于每类 CMT50 题目，可以预定义 validation contract：

```yaml
# 选择题 validation contract
choice_question_contract:
  required_evidence:
    - type: "per_option_analysis"
      must_show: "每个选项的独立支持/排除理由"
    - type: "consistency_check"
      must_show: "所选集合不自相矛盾"
  failure_modes:
    - "over_selection: 多选了无证据的选项"
    - "under_selection: 漏选了有证据的选项"
    - "wrong_set: 概念混淆导致选项完全错误"

# 符号题 validation contract
symbolic_question_contract:
  required_evidence:
    - type: "dimensional_check"
      must_show: "最终公式量纲正确"
    - type: "limit_check"
      must_show: "在已知极限下与标准结果一致"
    - type: "symbolic_verification"
      must_show: "SymPy 化简后与预期一致"
  failure_modes:
    - "missing_terms: 遗漏物理项"
    - "wrong_prefactor: 前置因子错误"
    - "normalization_error: 归一化错误"

# 数值题 validation contract
numeric_question_contract:
  required_evidence:
    - type: "independent_calculation"
      must_show: "code_runner 计算结果与推理一致"
    - type: "symmetry_check"
      must_show: "结果满足物理对称性"
    - type: "magnitude_sanity"
      must_show: "数值在合理范围内"
  failure_modes:
    - "unit_error: 单位换算错误"
    - "component_error: 向量部分分量错误"
    - "interpretation_error: 公式理解错误"
```

### 4.3 AITP 的"L2 Memory"设计对长期研究的启发

AITP 的 L2 memory 不是简单的"存储答案"，而是存储"可验证的研究状态"：

```yaml
L2_memory_entry:
  topic: "hubbard_model_finite_size"
  promoted_claim: "N=4 Hubbard 基态能量 E_0 = -2.0t (U=2)"
  scope: "仅适用于 half-filling, periodic boundary, 1D"
  evidence_refs: ["tool_run_001", "validation_001"]
  validation_refs: ["ed_diagonalization_check", "symmetry_check"]
  human_checkpoint: "reviewed_by_human_001"
  failure_modes:
    - "不适用于 N>8（ED 计算成本过高）"
    - "不适用于 U>10（需改用 DMRG）"
  provenance: "session_001, topic_hubbard_n4_u2"
  trust_level: "validated"  # vs "hypothesis" / "exploratory"
```

**应用到 CMT50**：

如果 Hakimi 在解 CMT50 时采用 AITP 风格的 L2 memory：

- 通过的题目不是"一次性正确"，而是"被验证的 claim"
- 失败的题目不是"丢弃"，而是"记录 failure mode"
- 重跑时可以从 L2 memory 恢复状态，而非从零开始
- 人工审核时可以查看完整的 evidence chain

---

## 五、综合对比表

| 对比维度 | 领域知识图谱（SCIGRAPHRAG 风格） | 研究过程图谱（AITP v5） | 对 CMT50 的价值 |
|----------|----------------------------------|------------------------|----------------|
| **核心实体** | Method, Model, Observable, Uncertainty | Claim, Evidence, Validation, ToolRun | 前者提供"知识"，后者提供"可信过程" |
| **核心关系** | estimates, suffers_from, solved_by | supported_by, derived_from, promoted_to | 前者是物理关系，后者是逻辑关系 |
| **构建时机** | 离线预构建 | 在线实时写入 | 前者快但可能过时，后者慢但精确 |
| **查询语言** | Cypher / SPARQL（图查询） | CLI / MCP（操作记录） | 前者适合"查知识"，后者适合"查进度" |
| **信任机制** | 无（知识本身不标记可信度） | 强（validation gates trust） | CMT50 需要后者来区分"猜测"和"理解" |
| **错误处理** | 无 | failure-mode review + trust audit | CMT50 的错误归因可以自动化 |
| **与 LLM 关系** | LLM 是消费者 | LLM 是生产者 | 两者都需要 |
| **最佳应用场景** | 概念查询、方法选择 | 研究执行、结果验证 | CMT50 需要两者结合 |
| **对"检索猜测"的防御** | 弱（知识可被复制） | 强（需要验证才能晋升） | AITP 的 validation 是核心防线 |
| **对"蒸馏理解"的促进** | 中（结构化知识促进理解） | 强（验证强制理解） | 两者结合最佳 |

---

## 六、对 Hakimi 路线图的修正建议

基于 AITP 的启示，修正之前的路线图：

### 原路线图（仅领域 KG）

```
Phase 1: 推理验证层 ──→ symbolic_verifier + option_evidence_tracker
Phase 2: 领域知识层 ──→ physics_knowledge_retriever + standard_result_crosscheck
Phase 3: 智能组织层 ──→ 动态工具链编排
```

### 修正路线图（领域 KG + AITP 过程层）

```
Phase 1: 推理验证层 ──→ symbolic_verifier + option_evidence_tracker
                        + 引入 AITP 风格的 validation contracts

Phase 2: 领域知识层 ──→ physics_knowledge_retriever (领域 KG)
                        + 引入 AITP 风格的 claim/evidence/validation 分离

Phase 3: 研究过程层 ──→ AITP 风格的 L2 memory + promotion packets
                        + failure-mode tracking + trust audits
                        + 动态工具链编排
```

### 具体修正

| 原建议 | 修正建议 | 理由 |
|--------|----------|------|
| 新增 `physics_knowledge_retriever` 返回知识卡片 | 知识卡片 + AITP 风格的 `evidence_record` | 不仅给知识，还要记录 Agent 如何使用知识 |
| 新增 `symbolic_verifier` 验证公式 | `symbolic_verifier` + `validation_contract` | 验证不是可选的，是晋升的必要条件 |
| 新增 `option_evidence_tracker` 追踪选项证据 | `option_evidence_tracker` + `claim_record` | 证据要绑定到具体 claim，不是孤立的 |
| 动态工具链编排 | 工具链编排 + `tool_run_record` | 每次工具调用都要记录输入/输出/状态 |
| 错误归因人工审计 | `failure_mode_packet` + `trust_audit` | 自动化记录失败模式，支持长期信任评估 |

---

## 七、一句话总结

> **领域知识图谱（如 SCIGRAPHRAG）回答"物理世界有什么知识"。**
> **AITP 回答"这个研究进行到哪了、哪些可信、哪些还只是假设"。**
>
> **对于 CMT50，前者让 Agent "知道更多"，后者让 Agent "更不容易自欺"。两者结合，才能既"解得出"又"解得可信"。**

---

*本分析基于 AITP-Research-Protocol v5 公开文档（bhjia-phys, 2026）和 MIT SCIGRAPHRAG（2025）研究。*
