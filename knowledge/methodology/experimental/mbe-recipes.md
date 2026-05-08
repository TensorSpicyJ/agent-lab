---
last_updated: 2026-05-08
---

# MBE 生长方法积累

## 标准 LSCO ALL-MBE 流程

### 衬底准备
- 衬底材料: SLAO (SrLaAlO4), LAO (LaAlO3), STO (SrTiO3)
- 取向: (001)
- 预处理: 参考 Xu 2022 APL Materials

### 生长策略
- 先长 LCO 母体标定 La/Cu 比例
- 找到稳定 La/Cu 基线后，再调 La/Sr 做 LSCO
- Cu 尽量保持不变，把 Sr 作为主调变量
- 一次生长一套条件，不在中途连续改多个参数

### 关键控制参数
- 衬底温度: 热电偶 + 红外双读
- 氧压: 生长氧压 vs 退火氧压 vs 降温氧压
- 源通量: La, Sr, Cu 各自的束流速率 (A/s) 和炉温
- 通量比: La/Cu, Sr/Cu, (La+Sr)/Cu
- 半单层停驻时间
- 退火: 温度、时间、氧压

## 表征手段

### XRD
- 2θ-ω 扫描 → c 轴参数
- Rocking curve → 结晶质量/disorder
- 倒空间 mapping → 应变状态（需要时可做）

### RHEED
- 生长过程实时监测
- 阶段识别: INI → 0.5 → 1.0 → ... → AFTER-ANNEALING → FIN
- 关键指标: 镜面反射强度、衍射斑锐度、Kikuchi 线

### PPMS 输运
- R-T: Tc onset, Tc50, Tc0, RRR
- Hall: 载流子类型和浓度
- I-V: 临界电流

## 自有工具链
- 样品索引: `experiment-data-center/data/metadata/web_entry.db`
- 生长数据库: `experiment-data-center/data/metadata/growth_conditions.csv`
- 束流记录: `experiment-data-center/data/metadata/source_flux_measurements.csv`
- 网页填写: `lsco-rx web-entry --open-browser` → http://127.0.0.1:8765/

## 经验教训
- 超薄样品(<6 u.c.)对生长条件波动极度敏感
- SLAO 封帽不是惰性的——会影响 c 轴参数和输运
- LCO 母体阶段的 RHEED 质量是后续 LSCO 超导质量的先决条件
