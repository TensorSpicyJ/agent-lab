# agent-lab

研究怎么做好的 agent，实验场 → 长期演进为自主研究 agent 的主仓库。

## 目录

| 目录 | 内容 |
|------|------|
| `design/` | 自主研究 agent 设计文档（架构、设计哲学、关键决策） |
| `knowledge/` | 统一研究知识层 — agent 的"脑"（4条研究线，理论实验一体） |
| `skills/` | 研究 agent 的能力技能（paper-to-insight、state-overview 等） |
| `research/` | 分析笔记：agent/harness 架构调研（AITP、Feynman、Forge、Anthropic 等） |
| `experiments/` | 可运行的实验 agent |
| `specs/` | harness 接口规范草案 |

## 架构概览

```
LIGHT GATES (只在 promotion/contradiction/publication 介入)
    ↑
CAPABILITY SKILLS (按需激活，上下文隔离)
    ↑
RESEARCH KNOWLEDGE LAYER (统一知识脑，理论实验不分家)
```

详见 `design/research-agent-design.md`。

## 快速开始

1. 读 `design/research-agent-design.md` 了解整体设计
2. 读 `knowledge/INDEX.md` 了解当前研究状态
3. 研究型任务时：先加载 `knowledge/lines/<line>/STATE.md`
4. 处理论文时：使用 `skills/paper-to-insight/SKILL.md`

## 研究线

| # | 研究线 | 类型 | 状态 |
|---|--------|------|------|
| 1 | LSCO 单层 | mixed | active（4假说, 7论文） |
| 2 | 超导二极管/隧道结 | mixed | seeding |
| 3 | 超导磁性材料 | mixed | seeding |
| 4 | 拓扑序 | theoretical | active（GSD=4 proven） |
