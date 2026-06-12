# RAG 得到的是什么结构？—— 从文本块到知识图谱的演进

> 基于科学/物理领域 RAG 最新研究（MIT SCIGRAPHRAG、Knowledge Graph RAG）
> 结合 CMT50 实验上下文
> 2026-06-06

---

## 一、RAG 的通用架构

RAG（Retrieval-Augmented Generation）的核心是**检索器 + 生成器**的两阶段架构：

```
┌─────────────────────────────────────────────────────────────┐
│  用户查询 (Query)                                           │
│     ↓                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   检索器     │ → │  检索结果    │ → │   生成器     │ │
│  │  (Retriever) │    │  (Context)   │    │  (Generator) │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│     ↑                       ↓                               │
│  向量数据库/知识库      注入提示词                          │
└─────────────────────────────────────────────────────────────┘
```

**关键问题**：检索器返回的"检索结果"（Context）是什么结构？这直接决定了生成器能"理解"到什么程度。

---

## 二、检索结果的四种结构层次

RAG 得到的结构不是单一的，而是一个从"原始"到"精炼"的光谱：

### Level 0: 原始文档（Raw Document）

```
结构：完整的 PDF/论文/教科书章节
长度：10,000–100,000+ tokens
优点：信息完整，无截断
缺点：远超上下文窗口；信息密度低；噪声大
适用：几乎不直接使用
```

### Level 1: 文本块（Text Chunks）—— 传统 RAG

```
结构：固定长度或语义边界的文本片段
示例：
  "变分蒙特卡洛（VMC）是一种基于变分原理的量子多体数值方法。
   它通过优化试探波函数来逼近基态能量。Reynolds 等人提出了..."
长度：200–1,000 tokens/块
索引方式：向量嵌入（Embedding）+ 余弦相似度检索
优点：实现简单；语义检索灵活
缺点：
  - 跨块信息断裂（公式的定义在块A，应用在块B）
  - 缺乏显式关系（不知道"这个方法"对应"那个结果"）
  - 容易检索到"相关但无关"的片段
```

**传统 RAG 的核心问题**：

> "RAG 依赖语义匹配局部文本块，但当相关信息跨越多个片段时，难以保持连贯上下文，导致碎片化表示，缺乏全局跨文档信息。" —— MIT SCIGRAPHRAG

### Level 2: 结构化文本块（Structured Chunks）—— 增强 RAG

```
结构：文本块 + 元数据 + 层级结构
示例：
  {
    "chunk_id": "CMT-ED-003",
    "source": "Grosso & Parravicini, Ch.4",
    "section": "Exact Diagonalization",
    "subsection": "Lanczos Algorithm",
    "text": "Lanczos 方法通过构建 Krylov 子空间...",
    "entities": ["Lanczos", "Krylov subspace", "tridiagonal matrix"],
    "formulas": ["H|v_n⟩ = α_n|v_n⟩ + β_n|v_{n-1}⟩ + β_{n+1}|v_{n+1}⟩"],
    "prerequisites": ["Hilbert space", "sparse matrix"],
    "applications": ["spin chains", "Hubbard model"]
  }
优点：保留文档结构；可过滤；可溯源
缺点：仍然是文本中心；关系是隐式的
```

### Level 3: 知识图谱（Knowledge Graph）—— Graph RAG

```
结构：实体（节点）+ 关系（边）+ 属性
示例：
  节点（实体）:
    - (Method: "VMC", description: "变分蒙特卡洛")
    - (Observable: "ground_state_energy")
    - (Paper: "Reynolds_1982")
    - (Uncertainty: "bias", type: "systematic")

  边（关系）:
    - (VMC) --[estimates]--> (ground_state_energy)
    - (Reynolds_1982) --[introduces]--> (VMC)
    - (VMC) --[suffers_from]--> (bias)
    - (bias) --[mitigated_by]--> (importance_sampling)

检索方式：图遍历（Graph Traversal）+ Cypher/SPARQL 查询
优点：
  - 显式关系："这个方法对应那个结果"
  - 跨文档连接：自动关联不同论文中的同一概念
  - 多跳推理：A→B→C 的链式推导
  - 可解释性：检索路径可追溯
缺点：构建成本高；需要领域 schema
```

### Level 4: 领域专用知识图谱（Domain-Specific KG）—— SCIGRAPHRAG

```
结构：预定义 schema 的知识图谱 + 领域实体类型

以粒子物理（LHCb）为例的 schema：
  实体类型:
    - paper: {arxiv_id, abstract, data_period, analysis_strategy}
    - observable: {name, description, type, standard_notation}
    - decay: {parent, children, production_mechanism}
    - uncertainty_source: {name, description, type}
    - method: {name, description}

  关系类型:
    - paper --[measures]--> observable
    - paper --[studies]--> decay
    - observable --[has_uncertainty]--> uncertainty_source
    - uncertainty_source --[treated_by]--> method

检索方式：自然语言 → Cypher 查询 → 子图提取 → LLM 生成
优点：
  - 领域精确：不会把"VMC 偏差"和"DQMC 符号问题"混淆
  - 全局视角：跨论文的系统性知识整合
  - 可验证：每个答案都有图谱路径支撑
```

---

## 三、科学/物理领域：什么结构最有效？

### 3.1 不同结构的适用场景

| 结构层次 | 最适合的场景 | CMT50 适用性 |
|----------|-------------|-------------|
| **文本块** | 通用问答、客服、简单事实查询 | ⚠️ 低 — CMT50 需要跨概念推理 |
| **结构化文本块** | 技术文档、手册、结构化报告 | 🟡 中 — 可改善检索精度 |
| **通用知识图谱** | 百科、常识、通用关系 | ⚠️ 低 — 缺乏 CMT 专业实体 |
| **领域专用 KG** | 科学研究、专业领域、多跳推理 | ✅ **高** — 匹配 CMT50 需求 |

### 3.2 为什么 CMT50 需要领域专用 KG？

CMT50 的题目特征：

| 特征 | 文本块 RAG 的问题 | 领域 KG 的解决 |
|------|------------------|---------------|
| "VMC 梯度估计量的偏差" | 可能检索到 VMC 介绍，但找不到"梯度"+"偏差"的关联 | KG 中 (VMC) --[gradient_estimator]--> (bias) 直接关联 |
| "Hubbard 模型 N=4 的基态" | 可能检索到 Hubbard 模型定义，但找不到 N=4 的具体结果 | KG 中 (Hubbard_model) --[ground_state]--> (energy_N4) |
| "DQMC 在长程相互作用下的符号问题" | 可能分别检索到"DQMC"和"长程相互作用"，但无法判断它们的关系 | KG 中 (DQMC) --[sign_problem]--> (long_range_interaction) 显式否定或条件关系 |
| "比较 DMRG 和 ED 在 dimer 链上的精度" | 需要跨两篇论文的信息整合 | KG 中 (DMRG) --[compared_with]--> (ED) --[on]--> (dimer_chain) |

---

## 四、从非结构化到结构化：RAG 得到的是什么？

### 4.1 构建流程

```
原始论文/教科书
    ↓
[文本提取] → 纯文本 + 公式 + 表格
    ↓
[分块/分区] → 段落、章节、公式块
    ↓
[实体识别] → 方法名、物理量、模型名、不确定性来源
    ↓
[关系抽取] → "A 方法用于估计 B 物理量"、"C 模型在 D 条件下有效"
    ↓
[图谱构建] → 节点 + 边 + 属性
    ↓
[跨文档归一化] → 同一概念在不同论文中的统一标识
    ↓
[查询接口] → 自然语言 → Cypher/SPARQL → 子图 → LLM
```

### 4.2 CMT 领域的具体实体类型建议

基于 CMT50 的错误归因，建议构建以下实体类型：

```yaml
# 方法层
methods:
  - name: "VMC"
    type: "variational_monte_carlo"
    properties:
      - trial_wavefunction
      - energy_estimator
      - optimization_scheme

  - name: "DMRG"
    type: "density_matrix_renormalization"
    properties:
      - bond_dimension
      - truncation_error
      - entanglement_entropy

  - name: "DQMC"
    type: "determinant_quantum_monte_carlo"
    properties:
      - sign_problem
      - hubbard_stratonovich_transform
      - imaginary_time

# 物理量层
observables:
  - name: "ground_state_energy"
    type: "energy"
    units: "eV"  # 或自然单位

  - name: "spin_correlation"
    type: "correlation_function"
    definition: "⟨S_i^z S_j^z⟩"

  - name: "entanglement_entropy"
    type: "entropy"
    definition: "S_A = -Tr(ρ_A log ρ_A)"

# 模型层
models:
  - name: "Hubbard_model"
    hamiltonian: "H = -t Σ⟨ij⟩ c_i† c_j + U Σ_i n_i↑ n_i↓"
    parameters: [t, U, N]
    limits:
      - condition: "U/t → 0"
        behavior: "metallic"
      - condition: "U/t → ∞"
        behavior: "Mott insulator"

  - name: "Heisenberg_model"
    hamiltonian: "H = J Σ⟨ij⟩ S_i · S_j"
    parameters: [J, N, spin]

# 不确定性/错误来源层
uncertainty_sources:
  - name: "VMC_bias"
    type: "systematic"
    cause: "finite_sample_size"
    mitigation: "importance_sampling"

  - name: "DMRG_truncation_error"
    type: "systematic"
    cause: "finite_bond_dimension"
    mitigation: "extrapolation"

  - name: "DQMC_sign_problem"
    type: "fundamental"
    cause: "fermionic_exchange"
    conditions:
      - "present_in: repulsive_hubbard"
      - "absent_in: attractive_hubbard"
      - "mitigated_by: auxiliary_field"

# 标准结果层
standard_results:
  - name: "1D_Hubbard_exact_solution"
    model: "Hubbard_model"
    dimension: 1
    method: "Bethe_ansatz"
    result: "E_0 = -4t ∫_0^∞ dω J_1(ω) / (ω(1 + exp(ωU/2t)))"
    reference: "Lieb & Wu, 1968"
```

### 4.3 关系类型建议

```yaml
relations:
  # 方法-物理量关系
  - type: "estimates"
    from: "method"
    to: "observable"
    properties: [bias, variance, computational_cost]

  - type: "suffers_from"
    from: "method"
    to: "uncertainty_source"
    properties: [severity, conditions]

  # 模型-方法关系
  - type: "solved_by"
    from: "model"
    to: "method"
    properties: [accuracy, applicable_regime]

  - type: "has_exact_solution"
    from: "model"
    to: "standard_result"
    properties: [dimension, parameter_regime]

  # 物理量-物理量关系
  - type: "derived_from"
    from: "observable"
    to: "observable"
    properties: [formula, assumptions]

  # 结果-验证关系
  - type: "verified_by"
    from: "standard_result"
    to: "method"
    properties: [agreement_level, discrepancy]
```

---

## 五、RAG 返回给 LLM 的最终结构

### 5.1 传统 RAG 的返回结构

```json
{
  "query": "VMC 梯度估计量的偏差来源",
  "retrieved_chunks": [
    {
      "text": "Reynolds 等人提出了...",
      "source": "paper_123",
      "similarity_score": 0.87
    },
    {
      "text": "在 VMC 中，梯度估计...",
      "source": "paper_456",
      "similarity_score": 0.82
    }
  ]
}
```

**问题**：LLM 看到的是两段"相关"的文本，但需要自己推断它们之间的关系。

### 5.2 Graph RAG 的返回结构

```json
{
  "query": "VMC 梯度估计量的偏差来源",
  "retrieved_subgraph": {
    "nodes": [
      {"id": "VMC", "type": "method", "name": "Variational Monte Carlo"},
      {"id": "gradient_estimator", "type": "concept", "name": "Gradient Estimator"},
      {"id": "bias", "type": "uncertainty_source", "name": "Bias"},
      {"id": "importance_sampling", "type": "method", "name": "Importance Sampling"}
    ],
    "edges": [
      {"from": "VMC", "to": "gradient_estimator", "relation": "uses"},
      {"from": "gradient_estimator", "to": "bias", "relation": "suffers_from"},
      {"from": "importance_sampling", "to": "bias", "relation": "mitigates"}
    ],
    "paths": [
      {
        "path": "VMC → gradient_estimator → bias",
        "explanation": "VMC 使用梯度估计量，梯度估计量存在偏差"
      },
      {
        "path": "importance_sampling → bias",
        "explanation": "重要性采样可以减轻偏差"
      }
    ]
  }
}
```

**优势**：LLM 看到的不是"相关文本"，而是"结构化关系"——可以直接用于推理。

### 5.3 领域专用 RAG（SCIGRAPHRAG 风格）的返回结构

```json
{
  "query": "VMC 梯度估计量的偏差来源",
  "cypher_query": "MATCH (m:Method {name: 'VMC'})-[:uses]->(c:Concept)-[:suffers_from]->(u:Uncertainty) RETURN m, c, u",
  "retrieved_knowledge": {
    "primary_entity": {
      "type": "Method",
      "name": "VMC",
      "properties": {
        "description": "变分蒙特卡洛",
        "trial_wavefunction": "optimized",
        "energy_estimator": "local_energy"
      }
    },
    "related_entities": [
      {
        "type": "Concept",
        "name": "gradient_estimator",
        "relation_to_primary": "uses",
        "properties": {
          "formula": "∂E/∂α = 2Re⟨ψ|H - E|∂ψ/∂α⟩",
          "finite_sample_variance": "high"
        }
      },
      {
        "type": "UncertaintySource",
        "name": "bias",
        "relation_to_primary": "suffers_from",
        "properties": {
          "type": "systematic",
          "cause": "finite_sample_size",
          "affected_observable": "gradient"
        }
      },
      {
        "type": "Method",
        "name": "importance_sampling",
        "relation_to_primary": "mitigates",
        "properties": {
          "target": "bias",
          "mechanism": "reweighting"
        }
      }
    ],
    "cross_document_evidence": [
      {
        "paper": "Reynolds_1982",
        "claim": "VMC gradient estimator is unbiased for exact wavefunction",
        "caveat": "biased for approximate wavefunction"
      },
      {
        "paper": "Umrigar_1993",
        "claim": "Importance sampling reduces gradient variance by O(N)",
        "caveat": "does not eliminate bias from wavefunction ansatz"
      }
    ],
    "provenance": [
      "arxiv:1234.5678",
      "arxiv:9012.3456"
    ]
  }
}
```

---

## 六、对 Hakimi/CMT50 的具体建议

### 6.1 不要给 LLM "文本块"

传统 RAG 返回的文本块对 CMT50 几乎无用，因为：

- CMT50 不是"事实查询"，而是"推理任务"
- 文本块缺乏显式关系，LLM 需要自己推断（容易出错）
- 文本块可能包含"相关但误导"的信息（如不同参数 regime 的结果）

### 6.2 给 LLM "结构化知识卡片"

建议的返回结构（"知识卡片"）：

```yaml
knowledge_card:
  query_type: "method_analysis"  # 或 "model_property", "comparison", "derivation"

  primary_entity:
    name: "VMC"
    type: "method"
    one_sentence_summary: "基于变分原理的量子多体随机采样方法"

  key_properties:
    - property: "trial_wavefunction"
      value: "需优化参数化形式"
      importance: "high"
    - property: "energy_estimator"
      value: "局部能量 ⟨ψ|H|ψ⟩/⟨ψ|ψ⟩"
      importance: "high"
    - property: "gradient_estimator"
      value: "∂E/∂α = 2Re⟨ψ|H - E|∂ψ/∂α⟩"
      importance: "medium"
      caveat: "对近似波函数有偏"

  related_methods:
    - name: "DQMC"
      relation: "alternative_for_finite_temperature"
      key_difference: "DQMC 无虚时间演化，但有符号问题"
    - name: "importance_sampling"
      relation: "enhancement"
      key_difference: "减少方差，但不消除偏差"

  standard_results:
    - result: "1D Heisenberg 基态能量 E_0 = -4ln2 · J"
      method: "Bethe_ansatz"
      vmc_accuracy: "~0.1% with sufficient samples"

  common_pitfalls:
    - pitfall: "忽略波函数 ansatz 的偏差"
      consequence: "能量估计偏低"
      detection: "检查能量随 ansatz 复杂度是否收敛"
    - pitfall: "样本不足导致梯度噪声"
      consequence: "优化停滞或发散"
      detection: "监控梯度方差"

  applicable_conditions:
    - "ground_state: yes"
    - "finite_temperature: no (use DQMC or QMC instead)"
    - "real_time_dynamics: no (use TDVP or tDMRG instead)"
    - "fermions: challenging (sign problem in some formulations)"

  source_provenance:
    - "Grosso & Parravicini, Solid State Physics, Ch.12"
    - "Foulkes et al., Rev. Mod. Phys. 73, 33 (2001)"
```

### 6.3 为什么这种结构促进"蒸馏理解"而非"检索猜测"

| 特征 | 促进"蒸馏理解" | 防止"检索猜测" |
|------|---------------|---------------|
| `one_sentence_summary` | 强制 LLM 用自己的话概括 | 防止直接复制文本 |
| `key_properties` + `caveat` | 暴露知识的边界条件 | 防止不加条件地套用 |
| `related_methods` + `key_difference` | 建立对比框架 | 防止张冠李戴 |
| `common_pitfalls` | 提供错误检测机制 | 防止盲目信任检索结果 |
| `applicable_conditions` | 明确适用范围 | 防止超范围应用 |
| `source_provenance` | 可验证、可溯源 | 防止幻觉 |

---

## 七、总结：RAG 得到的结构决定了 Agent 能做什么

| RAG 结构 | Agent 得到什么 | Agent 能做什么 | CMT50 适用性 |
|----------|---------------|---------------|-------------|
| **文本块** | "相关段落" | 关键词匹配、事实查找 | ❌ 不适用 |
| **结构化文本块** | "带元数据的段落" | 过滤、排序、溯源 | ⚠️ 有限 |
| **通用知识图谱** | "实体和关系" | 多跳推理、关系推断 | 🟡 部分适用 |
| **领域专用 KG** | "CMT 概念网络" | 专业推理、条件判断、方法选择 | ✅ **最佳** |
| **知识卡片** | "精炼的、带边界条件的知识单元" | 理解原理、避免陷阱、正确应用 | ✅ **最佳** |

**最终建议**：

> 对于 CMT50 这类研究级科学推理任务，RAG 返回的应该是**"知识卡片"**而非**"文本片段"**。每张卡片包含：实体定义、关键属性、适用条件、常见陷阱、相关概念、标准结果、来源溯源。这种结构迫使 LLM "理解"而非 "复制"，从而最大化"蒸馏理解"、最小化"检索猜测"。

---

*本分析基于 MIT SCIGRAPHRAG（2025）、Knowledge Graph RAG（2025）等最新研究，结合 CMT50 实验数据设计。*
