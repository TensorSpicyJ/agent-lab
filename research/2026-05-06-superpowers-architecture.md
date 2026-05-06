# Superpowers Agent Skill System — 架构分析

> 来源：superpowers v5.0.7 by Jesse Vincent / Prime Radiant

## 系统概览

14 个技能构成的完整软件工程方法论链：brainstorming → design → plan → dispatch → review → finish。自动触发，`using-superpowers` 要求在**任何**回复前调用。

## 技能定义结构

### SKILL.md 格式
- **Frontmatter**（仅两个字段）：`name`（字母+连字符，动名词）、`description`（"Use when..." 触发条件，**绝不**总结工作流——测试表明 Claude 会走捷径跳过正文）
- **正文**：Overview → When to Use（dot flowchart）→ 核心流程 → Common Mistakes / Red Flags → Integration（REQUIRED SUB-SKILL 标记）→ Real-World Impact

### 两种技能类型
- **刚性/纪律型**（TDD、debugging、verification）：Iron Law（`NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST`）、不可违反条款、理性化反驳表
- **柔性/流程型**（planning、executing、finishing）：分步工作流、决策树、集成点

## 多 Agent 编排

### dispatching-parallel-agents
**核心原则：** 一个 agent 一个独立问题域，并行派发。
- **硬约束：** 不可共享状态、不可顺序依赖、各自独立上下文
- **Prompt 结构：** 聚焦、自包含、明确输出格式、约束边界
- **禁止：** 多 agent 同时编辑相同文件或使用相同资源

### subagent-driven-development（推荐的执行模型）
**Per-task 循环：**
1. **Implementer subagent** → 实现 → 测试 → 提交 → 自评 → 报告状态（DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED）
2. **Spec reviewer** → 逐行对照 spec 检查 → 合规则通过，否则 implementer 修 → 循环
3. **Code quality reviewer** → 仅 spec 通过后才启动 → 检查代码质量 → 不通过则修 → 循环
4. 标记任务完成 → 下一个

**子 agent 状态处理阶梯：** DONE（继续）→ DONE_WITH_CONCERNS（读关注点）→ NEEDS_CONTEXT（补上下文）→ BLOCKED（升级：更多上下文 → 更强模型 → 拆子任务 → 人工干预）

**模型选择：** 机械任务用便宜模型、集成任务用标准模型、架构/审查用最强模型

**关键红旗：** 绝不同时派多个 implementer → 绝不跳过审查 → 绝不先做 code review 后做 spec review → 绝不让子 agent 读 plan（controller 提供全文）

## Plan 格式（writing-plans）

### Header（强制）
```markdown
# [Feature Name] Implementation Plan
> **For agentic workers:** REQUIRED SUB-SKILL: subagent-driven-development
**Goal:** 一句话
**Architecture:** 2-3 句
**Tech Stack:** 关键技术
```

### Task 结构
- 每个 task 是自包含单元，每个 step 是 2-5 分钟的动作
- 完整代码，无引用、无省略
- Checkbox 跟踪：`- [ ] **Step 1: Write the failing test**` + 完整代码
- **禁止占位符：** TBD、TODO、"implement later"、"similar to Task N"

### 自检清单
1. Spec 覆盖——每个 spec 要求是否有对应 task？
2. 占位符扫描——搜索红旗模式
3. 类型一致性——跨 task 签名/属性名匹配？

## 技能编排协议

### 技能依赖图
```
brainstorming（硬门：设计未批准前不可写代码）
  ├─→ using-git-worktrees（隔离工作区）
  ↓
writing-plans（设计→实现 task）
  ├─→ subagent-driven-development（推荐：每 task 全新子 agent）
  │     ├─ TDD implementer
  │     ├─ spec reviewer → code quality reviewer
  │     └─ final reviewer
  │       ↓
  │     finishing-a-development-branch
  │
  └─→ executing-plans（替代：线性、同 session、人类检查点）
        ↓
      finishing-a-development-branch
```

### 共享状态规则
- **子 agent 绝不继承 session 上下文** — controller 精确构造每个子 agent 需要的内容
- **Plan 文件**是唯一共享工件，承载上下文向前传递
- **Git commit** 作为 checkpoint
- **Git worktree** 提供文件系统隔离
- **TodoWrite** 跨技能共享任务跟踪

## 12 个可复用模式

| # | 模式 | 描述 |
|---|------|------|
| A | Iron Law | 绝对规则 + 不可违反条款，防止 agent 理性化绕过 |
| B | 理性化防御表 | 预列借口和反驳，按 Excuse→Reality 两列编排 |
| C | Red Flags: STOP | 列出 agent 可能欺骗自己的思维信号 |
| D | Dot flowchart | 用于决策点、循环终止条件、"A vs B"选择 |
| E | Announce at start | 强制 agent 声明使用的技能，建立可见性和问责 |
| F | Fresh context per agent | 子 agent 不继承父上下文，精确构造所需信息 |
| G | Two-pass review | spec 合规先于 code quality，绝不倒序 |
| H | 边界验证门 | 关键边界处插入显式 checkpoint，通过才能继续 |
| I | File-first task decomposition | 先定义文件结构再写 task，一个文件一个职责 |
| J | 子 agent 阻塞升级阶梯 | 上下文→更强模型→拆任务→人工 |
| K | 成本感知模型选择 | 便宜模型做机械活，最强模型做架构/审查 |
| L | 沉没成本显式提醒 | 直接面对心理陷阱："时间已经没了，选择是：删了重写还是保留不可信代码"|
