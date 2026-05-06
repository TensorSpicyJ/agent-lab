# Claude Code 源码泄露 — 架构分析

> 来源：2026.03.31 npm v2.1.88 Source Map 泄露，~1900 TS/TSX 文件、51.2 万行
> 安全研究员 Chaofan Shou 发现。社区数小时内 fork 出 claw-code（Python 重写，50K+ stars）

## 技术栈

- **UI**: React + Ink（终端渲染）
- **运行时**: Bun
- **核心模式**: REPL 循环，自然语言输入 + 斜杠命令

## 架构全景：12 层包装器

核心 loop 极其简单（`while(true)` in QueryEngine.ts 46K 行）。所有复杂度在外部 12 层渐进包装：

```
工具调度 → 规划 → 子 agent → 技能 → 上下文压缩 →
持久任务 → 后台任务 → agent 团队 → 团队协议 →
自主协调 → worktree 隔离
```

每层独立，添加功能 = 添加层，不碰核心 loop。

## 工具系统

40+ 独立 Tool 模块，每个工具有 ~20 个生命周期方法：
- `validateInput()` → `checkPermissions()` → `call()`
- **开放-封闭原则**：加功能 = 加工具，永不动核心 loop
- 类插件架构：文件读写、Bash、LSP、子代理、网页抓取

## 六层权限防御

```
项目/用户配置 allowlist
→ auto-mode 分类器
→ coordinator gate
→ swarm worker gate
→ 23 条 bash 安全规则
→ 交互式用户确认
↓
cch 加密认证（Bun native Zig HTTP stack 计算，验证请求来自未修改二进制）
```

每层独立失败，无单点绕过。

## 三层记忆架构

| Layer | 机制 | 持久性 | 作用 |
|-------|------|--------|------|
| L1 | `memory.md` 文件 | 跨会话持久 | 长期事实、架构决策、编码偏好 |
| L2 | grep 搜索层 | 会话内主动检索 | 按需检索相关代码 |
| L3 | **KAIROS 守护进程** | 后台持续运行 | 语义索引、autoDream 记忆巩固、焦点感知 |

记忆架构核心观点：**记忆即索引，非存储。** autoDream 将过期记忆视为负债主动清理。

## Multi-Agent 协调系统

- **Coordinator**: 被**剥夺直接文件访问权**，只能派发 worker、路由消息
- **Workers**: 继承父 prompt cache 前缀以降低派发成本（cache 复用）
- **通信**: 结构化 XML `<task-notification>` 回传结果
- **Bridge**: 连接 VS Code / JetBrains IDE

## 关键 Feature Flags

| Flag | 描述 |
|------|------|
| **KAIROS** | 守护进程：后台运行、autoDream 记忆巩固、焦点感知自主模式 |
| **Coordinator Mode** | 多 agent 协调 |
| **ULTRAPLAN** | 30 分钟云端推理会话 |
| **Undercover Mode** | Anthropic 员工公共仓库操作时自动激活，抹除 AI 痕迹，**无法手动关闭** |
| **ANTI_DISTILLATION** | 反蒸馏：API 请求注入假工具定义，污染竞品训练数据 |
| **CHICAGO** | 桌面控制（鼠标、键盘、剪贴板、截屏） |

## 上下文管理

- `autoCompact`: 自动压缩，9 段结构化压缩格式
- 曾有严重 bug：单会话连续失败 3,272 次，日浪费 ~25 万次 API 调用
- 侧面说明压缩是持续、有重试、高稳定性要求的基础设施

## 工程启示

1. **模型是商品，harness 是护城河。** 模型调用 1.6%，98.4% 是脚手架。泄露后数小时内社区重写出 claw-code（Python）和 Rust 重写版。
2. **工具系统的开放-封闭原则。** 每个工具有自己的 validate→checkPerm→execute 生命周期，加功能不碰核心。
3. **安全是分层防御，不是单点。** 六层权限 + 加密认证，每层独立失败。
4. **记忆是索引，不是存储。** 三层架构 + autoDream 主动清理过期记忆。
5. **Coordinator 被剥夺工具访问权。** 只协调、不执行——这个安全边界设计很精妙。
