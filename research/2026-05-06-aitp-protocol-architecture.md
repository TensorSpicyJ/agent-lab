# AITP 研究协议 — 架构分析

> 来源：AITP v2.0 brain-driven protocol

## 六阶段门控协议

默认路径：L0 → L1 → L3 → L4 → L2，L5 为可选写作阶段。L2 不是起点而是**目的地**——只有通过完整验证 pipeline 的 claims 才能到达。

### L0 — 源发现
- 注册所有证据来源：论文、预印本、书籍、数据、代码、实验
- Gate：`source_registry.md` 必须有 frontmatter（source_count > 0 + search_status）+ 三个指定标题 + L0/sources/ 下至少一个 .md 文件

### L1 — 阅读与框架
- 定义有界研究问题，5 个强制工件：question_contract、source_basis、convention_snapshot、derivation_anchor_map、contradiction_register
- Gate：逐个检查 5 个文件的存在性、frontmatter 字段、正文标题。全通过才能到 L3

### L3 — 推导（协议心脏）
- 5 个子平面顺序：ideation → planning → analysis → result_integration → distillation
- 每个子平面有活跃工件 + 技能文件 + 强制增量更新 `flow_notebook.tex`
- 后边允许回退：analysis 可退回 planning/ideation，result_integration 可退回 analysis
- 推导纪律：每步必须记录方程+理由+来源+假设依赖+开放缺口，缺失标为 non_auditable

### L4 — 验证
- 6 种结果：pass / partial_pass / fail / contradiction / stuck / timeout
- 按研究通道要求不同证据：numeric 必须 scripts+outputs，formal_theory 需要维度/对称性检查
- **关键设计：L4 pass 不推进到 L5，而是返回 L3 做 post-validation 分析**，人决定下一步

### L2 — 可信知识（目的地）
- 三步晋升门：request_promotion → resolve_promotion_gate（人批准）→ promote_candidate
- 2D 信任模型：trust_basis（validated）+ trust_scope（bounded_reusable）
- 冲突检测：同 candidate_id 不同内容写入 conflicts/ 而非覆盖

### L5 — 写作
- 5 个溯源工件：outline、claim_evidence_map、equation_provenance、figure_provenance、limitations
- Gate：L3/tex/flow_notebook.tex 必须存在才能进入

## MCP 集成

- 34 个工具，前缀 `mcp__aitp__aitp_*`，所有状态变更走 MCP gate check
- 三种集成模式：
  - **Pattern A**：按需加载（可选引用工具）
  - **Pattern B**：在 checkpoint 由技能指示调用
  - **Pattern C**：工作流已吸收到 AITP 技能的强制步骤中（不可跳过）

## 状态机设计

- Stage 存储在 `state.md` frontmatter，是硬状态
- Gate 评估是调用时计算（检查实际文件存在 + frontmatter 字段 + 标题完整性），而非"agent 说完成了"
- 过渡只能通过专用 MCP 工具，先查 gate 再更新 state.md
- SessionStart hook：每次新 session 检测活跃 topic → 评估 gate → 告诉 agent 该读哪个技能

## 8 个值得采纳的设计

1. **文件系统即状态数据库** — Markdown + YAML frontmatter，可 diff、可 grep、可版本控制
2. **Gate 机械化检查** — 检查文件存在/字段/标题，而非"agent 声称完成"，防止自认证
3. **质量检查在 harness 层而非 prompt 层** — MCP server 强制通道特定证据要求，prompt 可能被忽略但工具级阻止不能绕过
4. **信任边界的人类主权** — 三步晋升门 + 强制 AskUserQuestion 弹窗
5. **Hook 驱动的技能注入** — SessionStart 根据当前 stage 决定加载哪个技能文件
6. **强制后边路径** — L4 pass 后必须回 L3，防止过早封闭，"验证不是终点"

## 5 个待改进点

1. Gate 刚性 vs 研究流动性 — 5 个特定文件 + 特定字段对探索性想法来说文书负担重
2. L3 子平面粒度 — 5 个子平面 + 每步 LaTeX 更新有显著开销
3. MCP server God class — ~1990 行单文件混合多种关注点
4. 弱引用运行时集成 — knowledge-hub 并行系统与 brain MCP server 关系不清
5. 过度依赖人类注意力 — L3 每子平面需多轮 AskUserQuestion，自主循环仅覆盖 L3-L4
