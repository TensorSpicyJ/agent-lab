# Hakimi 版本迭代路线图 —— 从 "稳定做题" 到 "做对题"

> 基于 CMT50 完整 A/B 实验数据
> 当前基线：Hakimi v0.13.0 + DeepSeek v4-pro = 5/50
> 目标：分阶段突破 Layer 1→Layer 2→Layer 3 瓶颈
> 2026-06-06

---

## 一、当前状态诊断

### 1.1 能力分层现状

```
┌────────────────────────────────────────────────────────────┐
│ Layer 3: 领域知识层 (Domain Knowledge)                      │
│ 需要：CMT 专业知识、物理直觉、文献知识                      │
│ 当前：❌ 完全缺失 — 零工具支持                              │
│ CMT50 难度占比：~60%                                        │
├────────────────────────────────────────────────────────────┤
│ Layer 2: 推理执行层 (Reasoning Execution)                   │
│ 需要：符号计算、数值验证、量纲检查、极限验证                  │
│ 当前：⚠️ 部分有 code_runner，但未用于物理验证                │
│ CMT50 难度占比：~25%                                        │
├────────────────────────────────────────────────────────────┤
│ Layer 1: 任务组织层 (Task Orchestration)                    │
│ 需要：工作流管理、记忆、目标追踪                            │
│ 当前：✅ Hakimi v0.13.0 实验工具已覆盖                      │
│ CMT50 难度占比：~15%                                        │
└────────────────────────────────────────────────────────────┘
```

### 1.2 错误归因热力图

| 错误类型 | 数量 | 占比 | 对应层级 | 当前工具覆盖 |
|----------|------|------|----------|-------------|
| `choice_wrong_set` | 18 | 51% | Layer 2+3 | ❌ 无选项级验证 |
| `symbolic_formula_mismatch` | 12 | 34% | Layer 2+3 | ❌ 无符号计算验证 |
| `numeric_value_mismatch` | 5 | 14% | Layer 2 | ⚠️ 有 code_runner 但未用于验证 |
| `runtime_timeout` | 6-10 | — | Layer 1 | ✅ ON 模式已改善 |

**结论**：当前 85% 的错误集中在 Layer 2-3，而 Hakimi 的投资 100% 在 Layer 1。这是"优化了错误的东西"。

---

## 二、版本迭代路线图

### Phase 0: 立即修复（v0.13.1 — 本周）

**目标**：消除已知 harness 和格式问题，让实验数据更干净。

| # | 改进项 | 具体做法 | 预期收益 | 验证方法 |
|---|--------|----------|----------|----------|
| 0.1 | **缩短系统提示词** | 将 7 个实验标志的提示词描述从 ~3,000 字符压缩到 ~500 字符；移除冗余的 workflow-recipe 和 domain-profile 描述 | 减少 token 成本；降低注意力稀释；可能改善 #1 的 JSON 产出 | 重跑 #1，对比 JSON 产出率和延迟 |
| 0.2 | **强制最终 JSON 契约** | 在 prompt 中增加："Your final output MUST be a single JSON object on the last line. No text after it." | 消除 ON 模式的 JSON 格式失败 | 统计两模式 JSON 产出率 |
| 0.3 | **修复数据质量问题** | 隔离 #1 和 #37（data_source 高风险题），修复 gold/提示边界争议后再纳入评分 | 减少噪声，让能力评估更干净 | 人工审核 #1 和 #37 的 source row |
| 0.4 | **选择性启用实验标志** | 根据题目类型动态开关：选择题启用 research-ledger（帮助组织多选项分析）；符号题启用 physics-memory（帮助追踪中间公式） | 减少不必要的延迟和 token 开销 | 对比全量 ON vs 选择性 ON 的延迟和准确率 |

**Phase 0 预期总收益**：JSON 产出率从 80-88% → 90%+；延迟降低 20-30%；数据噪声减少。

---

### Phase 1: 推理验证层（v0.14.0 — 2-3 周）

**目标**：在 Layer 2 建立"自检机制"，让 Agent 在提交答案前能验证自己的推理。

这是**最关键的突破方向**。当前 Agent 纯靠 LLM 内部推理，没有外部验证闭环。

#### 1.1 新增工具：`symbolic_verifier`

| 属性 | 设计 |
|------|------|
| **功能** | 调用 SymPy 进行符号公式化简、求导、积分、极限计算 |
| **输入** | LaTeX 字符串形式的公式 + 操作指令（simplify / diff / limit / expand） |
| **输出** | 化简后的公式 + 中间步骤 |
| **触发时机** | Agent 在推导符号答案后，调用此工具验证公式是否自洽 |

**针对的错误**：`symbolic_formula_mismatch`（12/35）

**典型应用场景**：

```
Agent 推导得到：2^cn
→ 调用 symbolic_verifier: simplify(2^(c*n))
→ 工具返回：2^(c*n) （无法进一步化简）
→ Agent 意识到需要代入 c=1/2
→ 再次调用：substitute(2^(c*n), c, 1/2) → 2^(n/2)
→ 与 gold 2^{N/2-1} 对比，发现还差一个因子
→ 重新检查推导步骤...
```

**预期收益**：`symbolic_formula_mismatch` 从 12 → 6-8（减少 30-50%）

#### 1.2 新增工具：`dimensional_checker`

| 属性 | 设计 |
|------|------|
| **功能** | 检查物理公式的量纲一致性 |
| **输入** | 公式 + 各符号的量纲定义 |
| **输出** | 量纲分析结果：一致 / 不一致 + 具体量纲推导 |
| **触发时机** | 符号答案生成后，作为快速 sanity check |

**针对的错误**：`symbolic_formula_mismatch` + `numeric_value_mismatch`

**典型应用场景**：

```
Agent 推导 Hubbard 模型能量表达式
→ 调用 dimensional_checker
→ 发现结果量纲是 [Energy^2] 而非 [Energy]
→ 回溯检查，发现漏掉了平方根
```

**预期收益**：捕获约 30% 的符号/数值错误

#### 1.3 新增工具：`option_evidence_tracker`

| 属性 | 设计 |
|------|------|
| **功能** | 强制 Agent 对每个选项给出独立的"支持证据"和"排除证据" |
| **输入** | 题目 + 选项列表 |
| **输出** | 结构化证据表：每个选项的 {支持理由, 排除理由, 置信度} |
| **触发时机** | 选择题答案提交前，强制调用 |

**针对的错误**：`choice_wrong_set`（18/35）+ `choice_over_selected` + `choice_under_selected`

**典型应用场景**：

```
题目：哪些 VMC 估计量是无偏的？选项 a,b,c,d,e

Agent 原行为："感觉 a 和 b 对，选 a;b"
→ 强制调用 option_evidence_tracker
→ 输出：
  a: 支持="直接采样满足 E[O] = ⟨ψ|O|ψ⟩" 排除="无" 置信度=0.9
  b: 支持="..." 排除="..." 置信度=0.3
  c: 支持="无" 排除="需要辅助波函数" 置信度=0.1
  d: 支持="..." 排除="..." 置信度=0.8
  e: 支持="..." 排除="..." 置信度=0.7
→ Agent 重新评估，发现漏选了 d;e
→ 最终答案：a;d;e
```

**预期收益**：`choice_wrong_set` 从 18 → 10-12（减少 30-40%）

#### 1.4 增强现有工具：`code_runner` → `physics_calculator`

当前 `code_runner` 已存在，但 Agent 很少主动用它做物理验证。改进：

| 改进 | 具体做法 |
|------|----------|
| 预置物理计算模板 | 在 code_runner 中预置 NumPy/SymPy 的常用物理计算模板（如：Hubbard 模型对角化、VMC 能量估计、DQMC 符号检查） |
| 强制验证提示 | 在系统提示词中增加："对于数值答案，你必须使用 code_runner 进行至少一次独立计算验证" |
| 结果对比机制 | Agent 必须对比 LLM 推理结果和 code_runner 计算结果，不一致时重新检查 |

**针对的错误**：`numeric_value_mismatch`（5/35）

**预期收益**：`numeric_value_mismatch` 从 5 → 2-3（减少 40-60%）

#### Phase 1 预期总收益

| 错误类型 | 当前 | Phase 1 后（估算） | 减少 |
|----------|------|-------------------|------|
| `choice_wrong_set` | 18 | 10-12 | -33% to -44% |
| `symbolic_formula_mismatch` | 12 | 6-8 | -33% to -50% |
| `numeric_value_mismatch` | 5 | 2-3 | -40% to -60% |
| **物理类错误合计** | **35** | **18-23** | **-35% to -50%** |
| **预期总分提升** | **5/50** | **8-12/50** | **+60% to +140%** |

---

### Phase 2: 领域知识层（v0.15.0 — 1-2 个月）

**目标**：在 Layer 3 建立 CMT 领域知识支持，让 Agent 能"查资料"而非纯靠内部参数记忆。

#### 2.1 新增工具：`physics_knowledge_retriever`

| 属性 | 设计 |
|------|------|
| **功能** | RAG 检索 CMT 领域知识 |
| **知识源** | CMT-Benchmark 相关论文、标准教科书章节（如：Grosso & Parravicini 固体物理、Sachdev 量子相变）、arXiv 关键论文摘要 |
| **输入** | 查询关键词（如 "VMC gradient estimator bias", "DQMC sign problem long-range"） |
| **输出** | 最相关的 3-5 段知识摘要 + 来源引用 |
| **触发时机** | Agent 遇到不确定的物理概念时自动调用，或在推理开始时做背景检索 |

**关键设计决策**：

| 决策 | 选择 | 理由 |
|------|------|------|
| 知识库范围 | 聚焦 CMT 核心领域（HF/ED/VMC/DMRG/QMC/PEPS/SM） | 避免通用搜索的噪声；CMT50 题目高度聚焦 |
| 检索策略 | 混合：题目关键词 + Agent 推理中的不确定概念 | 比纯题目关键词更精准 |
| 引用透明度 | 必须返回来源，Agent 需在答案中引用 | 便于人工审核和错误归因 |
| 更新频率 | 静态知识库（季度更新）+ 动态 arXiv 摘要（月度） | 平衡稳定性和时效性 |

**针对的错误**：所有物理类错误，尤其是概念性错误（如 #8 DMRG 的 `['a']` vs `['d']` 完全无重叠）

**预期收益**：难以精确量化，但可能将"概念完全错误"的题目（如 #8, #13, #14）从"都错"转化为"部分对"

#### 2.2 新增工具：`standard_result_crosscheck`

| 属性 | 设计 |
|------|------|
| **功能** | 将 Agent 的推导结果与已知标准结果对比 |
| **知识源** | 预置的 CMT 标准结果库（如：Hubbard 模型精确解、Kitaev 模型的能谱、FQHE 的标度律） |
| **输入** | Agent 的公式/数值 + 题目类型标签 |
| **输出** | 匹配度评分 + 最接近的标准结果 + 差异分析 |
| **触发时机** | 符号/数值答案生成后 |

**典型应用场景**：

```
Agent 推导 Hubbard 环的基态能量
→ 调用 standard_result_crosscheck
→ 工具返回："你的结果 E = -4t 与 N=4, U=0 的精确解 E = -4t 匹配。但题目参数是 U=2, 请检查强耦合展开。"
→ Agent 意识到忽略了 U 项
```

**预期收益**：减少"与已知物理完全矛盾"的错误

#### Phase 2 预期总收益

| 指标 | Phase 1 后 | Phase 2 后（估算） |
|------|-----------|-------------------|
| 正确率 | 8-12/50 | 12-18/50 |
| 主要剩余错误 | 推导细节错误 | 超纲/前沿题目（CMT50 中 ~20% 题目可能超出任何静态知识库） |

---

### Phase 3: 智能组织层（v0.16.0 — 2-3 个月）

**目标**：让 Layer 1 从"固定实验工具"进化为"自适应任务编排"，根据题目特征动态选择工具链。

#### 3.1 动态工具链编排

当前所有题目使用相同的 25 个工具（ON 模式）。改进为**题目自适应**：

| 题目特征 | 激活工具子集 | 理由 |
|----------|-------------|------|
| 选择题 + 选项 > 5 个 | option_evidence_tracker + research-ledger | 需要严格的选项级验证 |
| 符号公式题 | symbolic_verifier + dimensional_checker + physics_knowledge_retriever | 需要符号验证和量纲检查 |
| 数值向量题 | physics_calculator + standard_result_crosscheck | 需要数值计算和结果对比 |
| 长推理链题（>10 步） | research-ledger + goal-command + physics-memory | 需要中间状态追踪 |
| 简单概念题 | 最小工具集（20 个默认工具） | 避免不必要的延迟和成本 |

**实现方式**：

```yaml
# 在 manifest.yaml 中增加工具链配置
tool_chain_profiles:
  choice_heavy:
    tools: [option_evidence_tracker, research_ledger]
    max_runtime_multiplier: 1.2
  symbolic:
    tools: [symbolic_verifier, dimensional_checker, physics_knowledge_retriever]
    max_runtime_multiplier: 1.5
  numeric:
    tools: [physics_calculator, standard_result_crosscheck]
    max_runtime_multiplier: 1.3
  long_reasoning:
    tools: [research_ledger, goal_command, physics_memory]
    max_runtime_multiplier: 2.0
```

**预期收益**：
- 平均延迟降低 20-30%（简单题不加载重型工具）
- 复杂题获得更多资源（长推理题分配更多时间和工具）
- token 成本降低 15-25%

#### 3.2 失败模式学习与自适应重试

| 功能 | 设计 |
|------|------|
| **失败检测** | 自动识别错误类型（choice_wrong_set / symbolic_mismatch / timeout） |
| **自适应重试** | 根据失败类型调整策略：选择题失败 → 强制 option_evidence_tracker；符号失败 → 强制 symbolic_verifier；超时 → 拆分推理步骤 |
| **历史学习** | 记录每道题的历史失败模式，下次遇到同类题时预加载对应工具 |

**预期收益**：将"一次性错误"转化为"可修复错误"

---

## 三、验证策略：每个 Phase 的退出标准

### Phase 0 退出标准

| 检查项 | 标准 | 验证方法 |
|--------|------|----------|
| JSON 产出率 | ON ≥ 90%, OFF ≥ 85% | 重跑 CMT50 全量 |
| 平均延迟 | ON 模式不高于 OFF 的 1.5 倍 | 对比 runtime_seconds 中位数 |
| 数据质量 | #1 和 #37 已修复或隔离 | 人工审核 source row |
| 无 harness 回归 | watchdog 脚本 100% 完成 | 检查 run-metadata.json 完整性 |

### Phase 1 退出标准

| 检查项 | 标准 | 验证方法 |
|--------|------|----------|
| symbolic_verifier 调用率 | 符号题调用率 ≥ 80% | 检查 stderr 中的工具调用日志 |
| option_evidence_tracker 调用率 | 选择题调用率 ≥ 80% | 同上 |
| physics_calculator 验证率 | 数值题验证率 ≥ 80% | 同上 |
| 错误类型转移 | `choice_wrong_set` + `symbolic_formula_mismatch` 合计减少 ≥ 30% | 对比 Phase 0 基线 |
| 总分提升 | 正确率 ≥ 8/50 | CMT50 全量重跑 |

### Phase 2 退出标准

| 检查项 | 标准 | 验证方法 |
|--------|------|----------|
| physics_knowledge_retriever 覆盖率 | 概念性题目检索率 ≥ 70% | 检查检索日志 |
| 知识引用准确性 | 返回的知识与题目相关度 ≥ 80%（人工抽样） | 抽样 10 题人工审核 |
| 总分提升 | 正确率 ≥ 12/50 | CMT50 全量重跑 |
| 与 Kimi 基线对比 | 超越 Kimi 2.6 优化后的 12/50 | 横向对比 |

### Phase 3 退出标准

| 检查项 | 标准 | 验证方法 |
|--------|------|----------|
| 动态工具链准确率 | 题目-工具链匹配准确率 ≥ 90%（人工抽样） | 抽样 20 题审核 |
| 平均 token 成本 | 不高于 Phase 2 的 1.2 倍 | 对比 API 账单 |
| 自适应重试成功率 | 重试后通过率 ≥ 30% | 统计重试题目的通过变化 |
| 总分提升 | 正确率 ≥ 15/50 | CMT50 全量重跑 |

---

## 四、风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| symbolic_verifier 引入新错误（SymPy 解析 LaTeX 失败） | 中 | 中 | 增加 LaTeX→SymPy 的 robust 转换层；失败时回退到纯 LLM 推理 |
| physics_knowledge_retriever 返回噪声知识 | 高 | 高 | 严格限制知识源范围；增加相关性评分阈值；低相关性时拒绝使用 |
| 工具链膨胀导致超时增加 | 中 | 中 | Phase 3 的动态编排就是为了解决这个问题；简单题用最小工具集 |
| 模型不主动调用新工具 | 高 | 高 | 在系统提示词中强制要求；对特定题目类型做工具调用约束 |
| 验证闭环增加延迟但准确率未提升 | 中 | 高 | 每个 Phase 都有明确的退出标准和 A/B 对比；未达标则回滚或调整 |

---

## 五、与 Kimi 基线的竞争定位

| 维度 | Kimi 2.6（优化后） | Hakimi 当前 | Hakimi Phase 1 后 | Hakimi Phase 2 后 |
|------|-------------------|------------|-------------------|-------------------|
| 正确率 | 12/50 | 5/50 | 8-12/50 | 12-18/50 |
| 超时率 | 低 | 中 | 低 | 低 |
| JSON 产出率 | 高 | 中 | 高 | 高 |
| 推理透明度 | 低（黑盒） | 中（有工具日志） | **高**（每步有验证记录） | **高** |
| 可解释性 | 低 | 中 | **高**（option_evidence_tracker 给出每选项理由） | **高** |
| 领域知识支持 | 无 | 无 | 无 | **有**（RAG） |
| 成本效率 | 中 | 低（提示词膨胀） | 中 | 中 |

**Hakimi 的差异化优势**：

Kimi 是"更强的模型本身"，Hakimi 应该走"**更强的推理基础设施**"路线：
- 不是让模型"更聪明"，而是让模型"**更不容易犯错**"
- 每步推理都有验证闭环
- 每个答案都有可追溯的证据链
- 每个错误都有可归因的失败模式

---

## 六、立即可以开始的 3 件事

### 今天就能做

1. **隔离 #1 和 #37**：从 CMT50 评分中临时移除这两题，减少数据噪声
2. **压缩实验标志提示词**：将 7 个标志的描述从 ~3,000 字符压缩到 ~500 字符
3. **增加强制 JSON 契约**：在 item prompt 中增加最终输出约束

### 本周就能做

4. **实现 option_evidence_tracker**：最简单的 Phase 1 工具，纯提示词工程即可原型
5. **跑 Phase 0 A/B**：重跑 CMT50，验证 JSON 产出率和延迟改善
6. **设计 symbolic_verifier 接口**：定义 SymPy 调用的输入输出 schema

### 本月就能做

7. **实现 symbolic_verifier + dimensional_checker**
8. **增强 physics_calculator 模板**
9. **跑 Phase 1 A/B**：验证错误类型转移和总分提升

---

*路线图基于 CMT50 的 50 题完整 A/B 实验数据，每个建议都有明确的错误归因支撑和可量化的验证标准。*
