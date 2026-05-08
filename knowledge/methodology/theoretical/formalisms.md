---
last_updated: 2026-05-08
---

# 常用理论框架

## 强关联电子 / 铜酸盐

### Five-band Hubbard model
- 使用场景: LSCO 电子结构（Makarov 2026 所用框架）
- 关键轨道: Cu 3d(x²-y²), O 2p(x), O 2p(y)
- 方法: 运动方程 Green's function + Hubbard 算子
- 关联论文: Makarov 2026 PRB

### t-J model / Zhang-Rice singlet
- 使用场景: 掺杂 Mott 绝缘体、铜酸盐超导配对机制
- 关键概念: Zhang-Rice singlet, 交换配对
- 关联论文: Zhang/Rice/Liu 2025

### Tight-binding for interfaces
- 使用场景: LSCO/LMO、LSCO/LCO 界面电荷转移
- 方法: 从 bulk Hamiltonian 出发，加 z 方向约束和界面 hopping

## 超导理论

### BKT transition
- 使用场景: 2D 超导、超薄 LSCO 的相位涨落
- 关键量: TBKT, 超流密度 ρs, I-V scaling exponent
- 关联论文: Baity 2016, Capone 2026

### Josephson junction / non-reciprocal transport
- 使用场景: 超导二极管效应
- 关键量: 临界电流不对称度 η = (Ic⁺ - Ic⁻)/(Ic⁺ + Ic⁻)
- 条件: 空间反演 + 时间反演对称性同时破缺

### Ginzburg-Landau for thin films
- 使用场景: 超薄极限下的序参量行为

## 拓扑序

### Toric code / Z2 gauge theory
- 数学结构: Z2 格点规范理论
- 基态简并度: 4 (在 torus 上)
- Anyon 类型: 1 (trivial), e (electric charge), m (magnetic flux), ψ (fermion)
- 形式化状态: Lean 4 中 GSD=4 已证明

### Kitaev quantum double
- 一般化: 从 Z2 扩展到任意有限群 G
- 当前状态: 尚未形式化

## 符号约定
- 待积累统一的符号约定文件
