# 交叉模式综合

> 对比三条线：Anthropic 官方实践、superpowers 技能系统、AITP 研究协议

## 共现模式（三条线都出现的）

### 1. 门控 (Gating)
| 来源 | 实现 |
|------|------|
| Anthropic | Prompt chaining 的 programmatic gate checks |
| Superpowers | Iron Law + verification gates（brainstorming 硬门、TDD 先看失败、spec review 先于 code review） |
| AITP | 机械化 gate 评估（检查文件存在/字段/标题）+ 过渡限制 |

**共同观点：** agent 的"我完成了"不能信任。必须用程序化/机械化的 gate check 来验证。

### 2. 上下文作为受限资源
| 来源 | 实现 |
|------|------|
| Anthropic | Progressive disclosure、MCP 超 10% 自动搜索模式、sub-agent 隔离、cache 优化 |
| Superpowers | Fresh context per agent、子 agent 绝不继承父 session 上下文 |
| AITP | Skill 注入按需加载（SessionStart hook 确定当前 stage → 只加载当前需要的技能文件） |

**共同观点：** 上下文是稀缺资源，要精确控制谁看到什么、什么时候看。

### 3. 文件作为 agent 间通信协议
| 来源 | 实现 |
|------|------|
| Anthropic | 多 agent 间用文件通信而非共享上下文窗口、"shift worker" 模式读 log → 选 feature → 实现 → commit |
| Superpowers | Plan 文件承载上下文从 writing-plans 到 subagent-driven-development、Git commit 作为 checkpoint |
| AITP | Markdown 文件系统即状态数据库、YAML frontmatter 为结构化字段、正文为内容 |

**共同观点：** agent 间不共享上下文窗口，通过结构化文件交接。

### 4. 人机边界设计
| 来源 | 实现 |
|------|------|
| Anthropic | 子 agent 不接触 plan 文件（controller 提供所需信息）、sprint contract 先谈判"什么是完成" |
| Superpowers | Human checkpoints between batches、AskUserQuestion at blocking points |
| AITP | 晋升门需要人类批准、三步 approve 不可跳过、Charter 第 5 条"晋升到可复用记忆非默认" |

**共同观点：** 人控制信任边界。AI 推导+验证，人决定采纳。

## 各线独特贡献

### Superpowers — 唯一做了"agent 心理学"
- 理性化防御表（Excuse→Reality 两列）
- Red Flags: STOP 列表（agent 欺骗自己的思维信号）
- 沉没成本显式提醒
- 这是 Anthropic 和 AITP 都没有的——对 agent 非理性行为的主动防御

### AITP — 唯一做了"知识状态模型"
- 按阶段的知识权威层级：L1 有来源无推导 < L3 推导中未验证 < L4 已验证 < L2 已晋升
- lane-specific evidence requirements（理论 vs 数值不同验证标准）
- 这是 Anthropic 和 superpowers 都没有的——对知识信任度的形式化

### Anthropic — 唯一做了"工程经济学"
- 成本感知模型选择（便宜模型做机械活、强模型做架构审查）
- 缓存优化 token 结构
- 工具策展是持续工程（定期砍掉死工具）
- 这是 superpowers 和 AITP 都没有的——对运维成本的系统思考

## 对 agent-lab 的直接启示

1. **Harness 的核心功能不是编排，是门控。** 编排 pattern 很简单（chain、route、parallel、orchestrate），真正的价值在于"agent 说完成时你真的能信吗"。

2. **好的 harness = 积累。** 每次 agent 犯错变成 rule/hook/skill，这本身就是一个值得设计的反馈循环。

3. **三个想做的实验方向：**
   - 把 superpowers 的理性化防御模式泛化到非 TDD 场景
   - 把 AITP 的机械化 gate 评估做成可复用的 harness 组件
   - 做成本感知的模型路由器（按任务复杂度自动选模型）
