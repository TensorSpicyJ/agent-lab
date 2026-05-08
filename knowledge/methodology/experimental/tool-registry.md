---
last_updated: 2026-05-08
---

# 实验工具注册表

experiment-analyzer skill 通过此文件发现和调用实验工具。新增工具时只需在此文件中添加条目。

## 模板: <工具类别>

### <工具名称>
- **命令**: `<cli-command>`
- **输入**: <输入文件或数据库路径>
- **输出**: <输出格式和位置>
- **适用场景**: <什么时候用这个工具>

---

## 当前注册工具

> 按实际实验环境添加。示例（LSCO 实验）：

### XRD 结构参数提取
- **命令**: `lsco-rx extract-xrd-structure --samples-db <db> --output <csv>`
- **输入**: web_entry.db
- **输出**: CSV (c-axis, peak positions, FWHM)
- **适用场景**: 单样品或批量 XRD 拟合结果入库
