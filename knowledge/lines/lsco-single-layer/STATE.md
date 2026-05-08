---
line: lsco-single-layer
type: mixed
last_updated: 2026-05-08
status: active
---

# LSCO 单层 — 研究状态

## 已知事实 (established)

### 来自实验
- LSCO 薄膜通过 ALL-MBE atomic layer-by-layer 工艺可稳定制备，关键步骤包括 substrate preparation、source calibration、post-growth annealing [来源: Xu 2022 APL Materials, confidence: high]
- LCO capping layer 会增强载流子局域化并压制超导——capping 不只是保护层 [来源: Sen 2017 PRB, confidence: high]
- LCO/LSCO(1.0) bilayer 超导主要局域在 LCO 层内，hole carriers 呈衰减分布延伸到约 5 u.c. [来源: Shi 2025 PRB, confidence: high]
- 超薄极限下 bilayer（总厚 1.5 u.c.）仍可保留超导 [来源: Shi 2025 PRB, confidence: high]
- 自有 #156 样品 XRD 完成拟合，c 轴参数已入库 [来源: in-house experiment-data-center, confidence: high]

### 来自理论/推导
- c 轴压缩通过抬升 a1g 轨道能量、增强与 b1g 能带相互作用，在欠掺杂区提升 Tc [来源: Makarov 2026 PRB Eq.12, confidence: high]
- 同时 c 轴压缩引起配对常数重整化，对 Tc 起抑制作用——两种效应竞争导致 Tc 对 c 轴的非单调依赖 [来源: Makarov 2026 PRB, confidence: high]
- LSCO 中可能存在 checkerboard 电子序，与 Zhang-Rice singlet 物理相关 [来源: Zhang/Rice/Liu 2025, confidence: medium]

## 活跃假说 (active hypotheses)

- **H1**: c轴压缩通过带结构重构提升Tc，在欠掺杂区更显著
  [evidence_type: theoretical]
  [支持: Makarov 2026 Eq.12]
  [待验证: 自有超薄LSCO样品的c轴参数 vs Tc correlation]

- **H2**: SLAO封帽层的应变效应在超薄区等效于负压
  [evidence_type: experimental]
  [支持: #156 XRD c轴数据]
  [反对/缺口: 尚缺直接应变测量/倒空间 mapping]

- **H3**: LSCO/LMO界面存在电荷转移导致的磁性重构
  [evidence_type: mixed]
  [支持: Tanaka 2024 XMCD（待入库）, 待推导界面电荷转移模型]
  [待验证: 缺界面敏感输运测量]

- **H4**: 超薄 LSCO(<4 u.c.)的超导抑制由无序局域化和界面 dead layer 共同决定，而非单一机制
  [evidence_type: mixed]
  [支持: Sen 2017 局域化证据, Shi 2025 界面载流子重分布]
  [待验证: 缺系统的厚度依赖输运+结构关联数据]

## 开放问题 (open questions)

- **Q1**: c轴参数与Tc的非单调关系在超薄区(<4 u.c.)是否仍然成立？(优先级: 高)
- **Q2**: 界面 dead layer 的厚度由应变主导还是电荷转移主导？(优先级: 高)
- **Q3**: 超薄 LSCO 中 BKT 转变 vs. 常规超导转变的 crossover 如何被 capping/strain 调控？(优先级: 中)
- **Q4**: LSCO 中 checkerboard 序与超导是竞争还是共存关系？(优先级: 中)

## 自有实验资产

- 样品编号体系: `experiment-data-center/data/metadata/external_samples.csv`
- 已有 XRD 分析样品: #156 (已完成), #014 (已完成), #139 (已完成)
- 已有 RHEED 数据: 多数样品有生长过程 RHEED 序列
- PPMS 输运数据: 部分样品有 R-T 和 Hall 数据
- 生长条件数据库: `experiment-data-center/data/metadata/growth_conditions.csv`

## 最近更新 (recent)
- 2026-05-08: 入库 Ahmad 2025 (LSCO superlattice Josephson), Baity 2016 (BKT), Liu 2026 (strain-correlated plasmons)
- 2026-05-06: 读完 Makarov 2026, Shi 2025, Sen 2017
- 2026-05-04: #156 XRD 拟合完成，c轴参数入库

## 下一步 (next actions)
- 补 #159 低温 R-T，与 #153 对比 c 轴差异 → 检验 H1
- 推 LSCO/LMO 界面 tight-binding 两层模型 → 支撑 H3
- 整理已有样品的 Tc vs. c-axis correlation → 检验 H1/H2
- 补 LSCO ultrathin 厚度依赖的 BKT 分析文献（baity 2016 等）
