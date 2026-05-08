---
line: lsco-single-layer
last_updated: 2026-05-08
---

# 假说跟踪 — LSCO 单层

## H1: c轴压缩通过带结构重构提升Tc，在欠掺杂区更显著
- **evidence_type**: theoretical
- **来源**: Makarov 2026 PRB
- **状态**: active
- **支持证据**:
  - Makarov Eq.12: 压缩→a1g抬升→与b1g相互作用增强→态密度增加 (confidence: high)
  - 自洽: 配对常数重整化提供抑制通道，自然解释非单调性 (confidence: medium)
- **反对/挑战证据**: 无直接反对
- **验证路径**: 测不同c轴参数样品的Tc，做 correlation plot；区分欠掺杂/最佳掺杂区
- **关联实验**: #153, #156, #159
- **关联推导**: derivations/tight-binding-2layer.md（待创建）
- **若成立**: 可作为超薄LSCO Tc调控的统一解释框架
- **若不成立**: 说明超薄区有额外机制（界面死层/无序效应）主导

## H2: SLAO封帽层的应变效应在超薄区等效于负压
- **evidence_type**: experimental
- **来源**: 自有 XRD 数据
- **状态**: active
- **支持证据**:
  - #156 XRD c轴数据 (confidence: high)
  - #158 XRD with thinner cap 的比较（待完成分析）
- **反对/挑战证据**:
  - 尚缺直接应变测量（RSM 或 HRXRD mapping）
- **验证路径**: 
  1. 系统比较不同封帽厚度的 c 轴参数
  2. 做倒空间 mapping 确认应变状态
  3. 与 uncapped 样品对比
- **关联实验**: #156, #158, 未来 uncapped 对照样品
- **关联推导**: 需要建立封帽→应变→c轴→Tc 的定量链
- **若成立**: 封帽不再是被动保护层，而是主动调控手段
- **若不成立**: c轴变化可能来自其他机制（氧化学计量比、阳离子互扩散）

## H3: LSCO/LMO界面存在电荷转移导致的磁性重构
- **evidence_type**: mixed
- **来源**: Tanaka 2024 XMCD + 自有理论构想
- **状态**: active
- **支持证据**:
  - Tanaka 2024 XMCD 在 LSCO/LMO 界面看到 Mn 磁信号变化（待入库详细分析）
  - 电荷转移理论预期: 界面 Mn 价态变化 (confidence: medium)
- **反对/挑战证据**: 无直接反对，但证据链还不完整
- **验证路径**:
  1. 入库并详细分析 Tanaka 2024 数据
  2. 建立 tight-binding 两层模型计算电荷转移量
  3. 设计自有 LSCO/LMO 样品的界面敏感输运测量
- **关联实验**: 暂无自有 LSCO/LMO 样品
- **关联推导**: derivations/interface-charge.md（待创建）
- **若成立**: 界面磁性→超导耦合成为可设计的调控自由度
- **若不成立**: 界面磁性可能太弱或被其他效应掩盖

## H4: 超薄 LSCO(<4 u.c.)的超导抑制由无序局域化和界面 dead layer 共同决定
- **evidence_type**: mixed
- **来源**: Sen 2017 + Shi 2025 + 自有实验经验
- **状态**: active
- **支持证据**:
  - Sen 2017: LCO capping→增强局域化→压制超导 (confidence: high)
  - Shi 2025: 界面 hole 分布决定超导位置 (confidence: high)
  - 经验: 超薄样品超导对生长条件极度敏感 (confidence: medium)
- **反对/挑战证据**: 尚缺定量的 dead layer 厚度 vs. disorder 贡献分解
- **验证路径**:
  1. 做系统的厚度依赖输运 (2-10 u.c.)
  2. 同时做 XRD 结构表征，关联 disorder (Rocking curve width)
  3. 比较不同 capping 材料 (SLAO vs LCO vs uncapped)
- **关联实验**: 已有部分不同厚度样品，需系统整理
- **若成立**: 超薄极限的优化应同时关注 disorder 最小化和界面载流子保留
- **若不成立**: 可能需要引入额外的超导抑制机制（如 quantum fluctuation/phase fluctuation）
