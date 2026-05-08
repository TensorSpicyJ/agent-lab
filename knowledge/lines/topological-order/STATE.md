---
line: topological-order
type: theoretical
last_updated: 2026-05-08
status: active
---

# 拓扑序 — 研究状态

> 长期理论积累线。当前以 Lean 4 形式化为主要推进方式。

## 已知事实 (established)

### 来自推导/形式化
- toric code 的基态简并度 GSD(T²) = 4 已在 Lean 4 中完整证明，无 `sorry` [来源: topological-order-lean, confidence: high]
- `GroundSpaceEquivalence` 定理：稳定子本征空间等价性已证明，包含 readout-pair 函数和标号扇区空间 [来源: topological-order-lean, confidence: high]
- `full_gsd_eq_four` 定理：对 n ≥ 2 且 (2:K) ≠ 0，`Module.finrank K (GroundSpace K) = 4` [来源: topological-order-lean, confidence: high]
- Z2 拓扑序 / toric code 的 anyon 模型已有明确的数学描述：4 种粒子类型 (1, e, m, ψ)

### 来自文献
- 拓扑序的核心概念框架已建立：基态简并度依赖于流形拓扑、anyon braiding statistics、edge theory/bulk correspondence

## 活跃假说 (active hypotheses)

- **H1**: toric code 的 Z2 拓扑序形式化可以扩展到更一般的 Kitaev 量子双模型
  [evidence_type: theoretical]
  [支持: 当前 toric code 基线已完成]
  [待验证: 需要一般化 group algebra 形式化框架]

- **H2**: 拓扑序的 anyon fusion/splitting 规则可以在 Lean 4 中作为类型类（typeclass）编码
  [evidence_type: theoretical]
  [状态: 设计阶段]

## 开放问题 (open questions)

- **Q1**: toric code 的 gapped edge theory（anyon condensation）能否在 Lean 4 中形式化？(优先级: 高)
- **Q2**: 从 toric code 到 Fibonacci anyon 的形式化路径是什么？(优先级: 中)
- **Q3**: 拓扑序形式化对物理直觉的反哺——能否从形式化过程中发现新的物理洞察？(优先级: 中)

## 形式化资产

- `topological-order-lean/` — 独立 Lean 工程仓库
- 核心命令: `lake update`, `lake exe cache get`, `lake build`
- checkpoint 文档: `docs/TORIC-CODE-CHECKPOINT.md`, `docs/FULL-GROUNDSPACE-EQUIVALENCE-SPIKE.md`
- 知识库: `D:\BaiduSyncdisk\code\OB_NOTE\MY NOTE\14-拓扑序学习库`

## 最近更新 (recent)
- toric code 基态简并度证明完成
- 仓库从知识库中独立为纯 Lean 工程 repo

## 下一步 (next actions)
- 将 toric code 的 anyon 类型（1, e, m, ψ）在 Lean 4 中编码
- 实现 braiding 操作的数学定义
- 探索 Kitaev 量子双模型的一般化框架
