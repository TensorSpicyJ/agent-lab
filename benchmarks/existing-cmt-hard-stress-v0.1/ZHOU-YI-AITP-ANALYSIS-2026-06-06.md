# 周毅 (AITP) 是怎么做的 —— 与领域知识图谱方法的对比

> 基于 AITP-Research-Protocol v5 最新公开文档（GitHub/bhjia-phys, 2026-06-06 版本）
> 结合 Hakimi 集成状态
> 2026-06-06

---

## 一、重大发现：AITP 与 Hakimi 已经在集成

通过直接读取 AITP 最新仓库文档，发现一个关键事实：

> **AITP v5 已经与 Hakimi 实现了运行时集成。**

文档原文：
- "Hakimi now auto-configures a WorkFrame-scoped typed session bridge"
- "Hakimi may compile it into blocking/current-turn call obligations"
- "Hakimi also has an opt-in real CLI smoke"
- "Hakimi's current bridge calls the same CLI surface with structured arguments"
- "Hakimi's automatic session bridge as runtime wiring"
- "Hakimi's `ResearchAction.execute_aitp_write_bridge` as a host execution path"

**这意味着**：周毅的 AITP 不是"另一个项目"，而是** Hakimi 正在接入的底层协议**。我们之前讨论的"领域知识图谱"和"AITP 研究过程图谱"不是二选一，而是** Hakimi 已经在走 AITP 路线**。

---

## 二、周毅 (AITP) 的核心做法

### 2.1 不是"知识图谱"，是"研究过程图谱"

AITP v5 的核心不是预构建的领域知识，而是**研究活动的 typed records**：

```
┌─────────────────────────────────────────────────────────────┐
│  AITP v5 Typed Kernel — 记录什么                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  组织层：topic, session, active claim                       │
│  内容层：definitions, physics objects, object relations      │
│  证据层：evidence, code state, tool recipes/runs            │
│  来源层：reference locations, source assets (论文/笔记/代码)  │
│  验证层：validation contracts, validation results           │
│  信任层：failure-mode review, promotion packets, L2 memory │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 关键创新：Typed Process Graph

AITP v5 最新实现了 `process_graph_slice`，将 typed records 编译成**过程图谱**：

```
aitp-v5 graph slice <session-id>

返回：
  - nodes:  typed records 的节点
  - edges:  记录间的关系
  - source backtrace: 来源回溯
  - relation neighborhoods: 关系邻域
  - open obligations: 未完成的义务
  - trust-boundary reasons: 信任边界原因
  - recommended research moments: 推荐的研究时刻
  - moment_policy.decisions: 决策列表（required_now / required_before_trust_change）
```

**这与领域 KG 的根本区别**：

| | 领域 KG（SCIGRAPHRAG） | AITP Process Graph |
|---|---|---|
| 节点是什么 | 物理实体（VMC, Hubbard 模型） | 研究记录（claim, evidence, tool run） |
| 边是什么 | 物理关系（estimates, suffers_from） | 逻辑关系（supported_by, derived_from） |
| 何时构建 | 离线预构建 | 研究过程中实时生成 |
| 查询什么 | "VMC 怎么估计能量？" | "我上次验证到哪了？下一步该做什么？" |

### 2.3 关键创新：Source Asset 注册

AITP v5 可以注册**来源资产**：

```
aitp-v5 asset register

可注册：
  - papers（论文）
  - lectures（讲义）
  - notes（笔记）
  - code repositories（代码仓库）
  - snapshots（快照）
  - datasets（数据集）
  - generated artifacts（生成的工件）

每个资产获得：
  - orientation-only identity
  - hash
  - version anchor
  - source/code/artifact links
```

**这与 RAG 的区别**：

| | 传统 RAG | AITP Source Asset |
|---|---|---|
| 如何处理来源 | 文本块嵌入向量库 | 注册为带身份、哈希、版本的资产 |
| 引用方式 | "根据相关文本..." | "根据 source asset X 的 evidence record Y" |
| 信任度 | 无（所有文本同等权重） | 有（需通过 validation 才能用于 claim） |

### 2.4 关键创新：Exploratory Research Graph

AITP v5 可以记录**探索性研究**：

```
aitp-v5 exploration record

记录：
  - source assets（来源资产）
  - question decomposition（问题分解）
  - relation-path brainstorming（关系路径头脑风暴）
  - backtrace steps（回溯步骤）
  - steering checkpoints（导向检查点）

状态：orientation-only（不直接作为证据）
```

**这解决了什么问题**：Agent 的"思考过程"被记录下来，但**不自动成为可信证据**。只有经过 validation 的才能晋升。

### 2.5 关键创新：Validation Contract

AITP v5 的验证合约是**强制性的信任门槛**：

```
创建验证合约：
  aitp-v5 validation contract create

记录验证结果：
  aitp-v5 validation result record

规则：
  - tool run 本身不足以信任
  - 高风险工具证据必须引用 passed validation results
  - 部分验证可以记录进度，但不能晋升整个 claim
  - promotion packets 必须命名已知的 failure modes
  - 如果 claim 有最强 failure mode，高风险晋升需要 failure-mode review checkpoint
```

**这与我们之前讨论的"validation contract"完全一致**——说明这个方向是对的，且已经在 AITP 中实现。

### 2.6 关键创新：QSGW Cockpit（研究驾驶舱）

AITP v5 最新实现了 `qsgw-cockpit`：

```
aitp-v5 status qsgw-cockpit

生成：
  - topic-local final/diagnostic lane manifest（通道清单）
  - plot guard（绘图守卫）
  - dashboard dry-run（仪表板干运行）
  - 发现下游 lane_manifest_current.json 和 aitp_intake_current.jsonl
```

**这解决了什么问题**：研究状态的可视化和监控，防止"盲目推进"。

---

## 三、AITP 与 Hakimi 的集成方式

### 3.1 Hakimi 的 AITP 桥接

根据 AITP 文档，Hakimi 的集成包括：

```
1. Hakimi 自动配置 WorkFrame-scoped typed session bridge
2. 读取 process_graph_slice
3. 编译 moment_policy.decisions 成 required call obligations
4. 暴露 model-facing AITP write-bridge execution
   - exploratory records（探索记录）
   - source assets（来源资产）
   - proof obligations（证明义务）
   - validation contracts/results（验证合约/结果）
   - human checkpoints（人工检查点）
```

### 3.2 Hakimi 的最终门控（Final Gate）

```
Hakimi 使用 moment_policy.decisions 进行 final gate checks：
  - 如果 required calls 未通过且未显式 blocked
  - 则 downgrade trust-sensitive answers（降级信任敏感答案）
  - 或要求记录 blocker
```

**这意味着**：AITP 的验证要求**直接约束 Hakimi 的输出**——如果某个 claim 需要 validation 但未完成，Hakimi 会被强制降级答案的信任度。

### 3.3 运行时入口点合约

AITP 定义了 Hakimi 应消费的稳定合约：

| Contract Key | CLI 模板 | MCP Tool | Surface |
|---|---|---|---|
| `process_graph_slice` | `aitp-v5 graph slice <session-id>` | `aitp_v5_get_process_graph_slice` | process_graph_slice |
| `record_evidence` | `aitp-v5 evidence record <args>` | `aitp_v5_record_evidence` | evidence_record |
| `record_tool_run` | `aitp-v5 tool run record <args>` | `aitp_v5_record_tool_run` | tool_run_record |
| `record_validation_result` | `aitp-v5 validation result record <args>` | `aitp_v5_record_validation_result` | validation_result_record |
| `create_validation_contract` | `aitp-v5 validation contract create <args>` | `aitp_v5_create_validation_contract` | validation_contract_record |
| `request_human_checkpoint` | `aitp-v5 checkpoint request <args>` | `aitp_v5_request_human_checkpoint` | human_checkpoint_record |

---

## 四、对比：周毅 (AITP) vs 我之前建议的"领域知识图谱"

### 4.1 根本差异

| 维度 | 我之前建议的领域 KG | 周毅 (AITP) 的做法 |
|------|-------------------|-------------------|
| **核心实体** | Method, Model, Observable, Uncertainty | Claim, Evidence, ToolRun, Validation |
| **核心关系** | estimates, suffers_from, solved_by | supported_by, derived_from, promoted_to |
| **知识来源** | 预构建的教科书/论文知识库 | 研究过程中实时注册的 source assets |
| **信任机制** | 我假设的"知识卡片带 caveat" | 强制 validation contract + promotion gate |
| **错误处理** | 我假设的"common_pitfalls 字段" | failure-mode review packets + trust audits |
| **与 Agent 关系** | Agent 消费知识 | Agent 生产记录，受信任门控约束 |

### 4.2 我之前建议的哪些与 AITP 一致

| 我的建议 | AITP 实现 | 一致性 |
|----------|----------|--------|
| validation contract | `aitp-v5 validation contract create` | ✅ 完全一致 |
| claim/evidence/validation 分离 | AITP v5 核心设计 | ✅ 完全一致 |
| failure-mode tracking | `failure-mode review packets` | ✅ 完全一致 |
| L2 memory | `promotion packets + L2 memory entries` | ✅ 完全一致 |
| 知识卡片 schema | AITP 的 typed records | ⚠️ 方向一致，但 AITP 更关注过程而非知识内容 |
| 领域 KG 实体类型 | AITP 的 physics objects | ⚠️ AITP 有 physics objects，但不是预构建 KG |

### 4.3 我之前建议的哪些与 AITP 不一致

| 我的建议 | AITP 做法 | 差异 |
|----------|----------|------|
| 预构建 CMT 领域 KG | 不预构建 KG，而是注册 source assets | AITP 不维护"领域知识图谱" |
| 返回"知识卡片"给 LLM | 返回 process_graph_slice + moment_policy | AITP 给 Agent 的是"下一步该做什么"而非"知识内容" |
| physics_knowledge_retriever | literature intake（保守取向） | AITP 的文献摄入是 orientation-only，不直接用于 claim |
| 动态工具链编排 | moment_policy.decisions | 方向一致，但 AITP 的决策来自过程图谱而非题目类型 |

---

## 五、关键洞察：AITP 解决的是"过程可信"，不是"知识覆盖"

### 5.1 CMT50 的真正问题是什么？

回顾 CMT50 实验：

| 问题 | 根因 |
|------|------|
| Agent 给出答案但无法解释 | claim/evidence/validation 未分离 |
| 答案错误但不知道错在哪 | 无 failure-mode tracking |
| 同一题目多次运行结果不同 | 无 session/topic 恢复机制 |
| "看起来对" 的答案被信任 | 无 validation gates |
| 长推理链超时后无中间状态 | 无 tool run 记录 |

**AITP 的设计恰好针对这些问题**——不是通过"给 Agent 更多知识"，而是通过"强制 Agent 记录和验证每一步"。

### 5.2 为什么 AITP 不构建领域 KG？

周毅的 AITP 明确区分了：

```
Authoritative（权威）：
  - typed v5 kernel records
  - validation contracts and results
  - evidence records linked to sources, code states, tool runs

Orientation-only（仅供参考）：
  - generated session/workspace summaries
  - workspace replay packets
  - Obsidian review views
  - README and planning docs
  - external note pointers and reference locations
```

**关键洞察**：AITP 认为"外部知识"（如教科书、论文）本身是 orientation-only 的，**不能自动成为证据**。只有经过 validation 的才能进入信任体系。

这与我的"知识卡片"设计有本质区别：
- 我的"知识卡片"假设"给 LLM 更好的结构化知识"能提升推理
- AITP 假设"给 LLM 知识不够，必须强制验证闭环"才能提升可信度

### 5.3 AITP 对 CMT50 的启示

如果 Hakimi + AITP 解 CMT50，流程应该是：

```
1. 创建 topic: "cmt-hard-research-50"
2. 对每道题创建 claim: "Problem X 的答案是 Y"
3. 创建 validation contract: "需要 symbolic_verifier 验证符号答案"
4. Agent 推理并记录：
   - evidence record（推理步骤）
   - tool run record（如 code_runner 执行）
   - reference location（引用的 source asset）
5. 如果 validation 通过 → promotion packet → L2 memory
6. 如果 validation 失败 → failure-mode review → 记录错误类型
7. 最终答案附带 trust level（validated / hypothesis / exploratory）
```

**这与 Kimi 基线的根本区别**：
- Kimi 基线：Agent 直接给答案，无验证，无记录
- AITP 流程：Agent 给答案 + 完整证据链 + 验证状态 + 信任等级

---

## 六、修正后的诚实结论

### 6.1 我之前建议的"领域知识图谱"方向

**部分正确**：
- 结构化知识比文本块更好 → 有 SCIGRAPHRAG 支撑
- validation contract 能减少错误 → 与 AITP 完全一致
- claim/evidence/validation 分离 → 与 AITP 完全一致

**部分错误**：
- "预构建 CMT 领域 KG" → AITP 不这么做，而是注册 source assets
- "返回知识卡片给 LLM" → AITP 返回的是 process_graph_slice（下一步该做什么）
- "知识卡片促进蒸馏理解" → 未验证的假设

### 6.2 周毅 (AITP) 的做法更根本

AITP 不试图"让 Agent 知道更多物理知识"，而是：

> **"让 Agent 的每一步推理都可记录、可验证、可溯源、可审计。"**

这与 CMT50 的实验数据更吻合：
- CMT50 的瓶颈不是"知识不足"（Kimi 已经能推导出部分答案）
- CMT50 的瓶颈是"推理过程不可信"（无法区分猜测和理解、无法追溯错误）

### 6.3 对 Hakimi 的修正建议

| 原建议 | 修正建议 |
|--------|----------|
| 构建 CMT 领域 KG | **接入 AITP v5**，使用其 source asset 注册机制 |
| 返回知识卡片 | **消费 AITP process_graph_slice**，获取 moment_policy.decisions |
| 新增 symbolic_verifier | **通过 AITP validation contract** 强制验证 |
| 新增 option_evidence_tracker | **通过 AITP evidence record** 记录每选项理由 |
| 动态工具链编排 | **遵循 AITP moment_policy** 的 required calls |

---

## 七、一句话总结

> **周毅 (AITP) 的做法不是"给 Agent 更好的知识图谱"，而是"给 Agent 推理过程加上不可篡改的审计链"。**
>
> **对于 CMT50，这意味着：不是让 Agent "知道更多物理"，而是让 Agent "证明它真的理解了"——通过 validation contracts、tool run records、failure-mode reviews 和 trust gates。**
>
> **而且 Hakimi 已经在集成 AITP v5，这意味着这个方向不是"未来可能做"，而是"正在发生"。**

---

*本分析基于 AITP-Research-Protocol v5 最新公开文档（GitHub/bhjia-phys, 2026-06-06 版本）的直接读取。*
