---
last_updated: 2026-05-08
---

# 实验工具注册表

experiment-analyzer skill 通过此文件发现和调用实验工具。新增工具时只需在此文件中添加条目。

## XRD 分析

### 提取 XRD 结构参数
- **命令**: `lsco-rx extract-xrd-structure --samples-db <db_path> --output <output_csv>`
- **输入**: `experiment-data-center/data/metadata/web_entry.db`
- **输出**: CSV（c轴参数、峰位、FWHM）
- **适用场景**: 单样品或批量 XRD 拟合结果入库

### 批量 XRD 拟合报告
- **命令**: 参考 `experiment-data-center/reports/xrd-reports/` 下的分析 note
- **输入**: XRD 原始数据文件（.ras 或 .csv）
- **输出**: Markdown 分析报告
- **适用场景**: 单样品详细 XRD 分析

## PPMS 输运

### 索引 PPMS 数据
- **命令**: `lsco-rx index-ppms --ppms-root <path> --output <csv>`
- **输入**: PPMS 原始数据目录
- **输出**: `ppms_bridge_summary.csv`
- **适用场景**: 批量扫描 PPMS 数据，提取输运指标

### 合并输运到样品表
- **命令**: `lsco-rx apply-ppms --samples-db <db_path> --summary <csv>`
- **输入**: web_entry.db + ppms_bridge_summary.csv
- **输出**: 更新后的样品数据库
- **适用场景**: 将输运指标（Tc, RRR, transition fraction）关联到样品

## RHEED 图像

### 提取 RHEED 特征
- **命令**: `lsco-rx extract-rheed --samples-db <db_path> --output <csv>`
- **输入**: web_entry.db（含 rheed_path）
- **输出**: RHEED 特征 CSV
- **适用场景**: 单帧 RHEED 图像的亮度/梯度/质心等特征提取

### 提取 RHEED 序列特征
- **命令**: `lsco-rx extract-rheed-sequence --frames <csv> --output <csv>`
- **输入**: `rheed_frames.csv`
- **输出**: 序列特征 CSV
- **适用场景**: 生长过程 RHEED 轨迹的时序特征

## 生长数据库

### 查看生长条件
- **方式**: 直接读取 `experiment-data-center/data/metadata/growth_conditions.csv`
- **输入**: 样品 ID
- **输出**: 生长条件行
- **适用场景**: 需要知道某样品的生长参数（温度、氧压、通量比）

### 查看束流记录
- **方式**: 直接读取 `experiment-data-center/data/metadata/source_flux_measurements.csv`
- **输入**: 测量组 ID 或日期范围
- **输出**: 束流历史记录
- **适用场景**: 追溯生长时的源通量状态

## 网页入口

- **命令**: `lsco-rx web-entry --open-browser`
- **URL**: http://127.0.0.1:8765/
- **适用场景**: 需要人工填写实验条件时
