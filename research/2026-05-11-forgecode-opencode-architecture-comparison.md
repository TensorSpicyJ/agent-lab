# ForgeCode vs OpenCode — 完整架构对比

> 来源：ForgeCode (Rust, 19 crates) 和 OpenCode (TypeScript/Bun, monorepo) 源码逐层分析
> 日期：2026-05-11

---

## 一、ForgeCode 架构（5 层）

### Layer 0: 原子类型 (`forge_domain`)

整个系统的词汇表。没有行为，只有数据定义：

```rust
AgentId("forge")          // newtype，带类型的字符串
ModelId("deepseek-v4-pro")
ProviderId("deepseek")
ToolName("read")
```

Agent 本身是纯数据：
```rust
Agent {
    id: AgentId,
    provider: ProviderId,          // 用什么 API
    model: ModelId,                // 用什么模型
    system_prompt: Template,       // Handlebars 模板，运行时渲染
    tools: Vec<ToolName>,          // 工具白名单（支持 glob："mcp_*"）
    max_turns: u64,
    max_tool_failure_per_turn: usize,
    max_requests_per_turn: usize,
    temperature: f64,
    compact: Compact,
    custom_rules: String,          // 注入 prompt 的自定义规则
}
```

工具是 enum，17 个变体：
```rust
enum ToolCatalog {
    Read | Write | Shell | FsSearch | SemSearch | Patch | Remove |
    Fetch | Followup | Plan | Skill | TodoWrite | TodoRead | Task | ...
}
```

**关键：Agent 不是代码，是数据。新 agent = 填 struct，不写逻辑。**

### Layer 1: Trait 接口

定义能力但不定义实现（DI 层）：

```rust
trait ChatRepository {
    async fn chat(model, context, provider) -> Stream<ChatCompletionMessage>;
}
trait ProviderRepository {
    async fn get_provider(id) -> Provider;
    async fn upsert_credential(credential) -> ();
}
```

### Layer 2: Service 实现 (`forge_services`)

把 trait 变成能跑的东西：

- `ProviderService` — 从 provider.json 读取 30+ provider 定义，构建 HTTP client
- `AgentRegistry` — 从 .md 文件加载 agent 定义
- `PolicyService` — 权限三态判决（Allow/Deny/Confirm）
- `ContextEngine` — 语义搜索索引

### Layer 3: 编排层 (`forge_app`) ← 核心

**Orchestrator（核心 loop）：**

```
while !should_yield {
    ① 保存对话状态到磁盘
    ② Hook: Request 事件（compaction 检查）
    ③ Transform pipeline: SortTools → NormalizeArgs → ImageHandling → DropReasoning
    ④ LLM 调用（带重试 + 流式输出）
    ⑤ Hook: Response 事件（doom loop 检测）
    ⑥ 执行工具：Task 工具并行，其余顺序执行
    ⑦ 错误追踪：失败工具注入 "你还剩 X 次尝试"
    ⑧ 追加到上下文
    ⑨ 检查退出条件（finish_reason=Stop、max_requests、max_failures）
    ⑩ Hook: End 事件（可追加消息 → loop 重入！）
}
```

**ToolRegistry（三级派发）：**
```
call(tool_name) →
  ① ToolCatalog enum → 匹配？→ tool_executor
  ② AgentExecutor → 匹配？→ 子 agent
  ③ MCPExecutor → 匹配？→ MCP 外部服务
  ④ 返回错误
```

权限检查在每次工具执行前：
```
check_tool_permission() → PermissionOperation 映射 →
  Allow → 执行
  Deny  → 拒绝
  Confirm → 弹窗（Accept / Reject / Accept & Remember）
```

**Hook 系统：** 6 个生命周期事件，handler 通过 `.zip()` `.and()` 组合。End hook 可追加消息让 loop 重入。

**Skill 系统：** 三级渐进披露（元数据 ~100 words → 正文 <5K → 资源按需）。加载优先级：CWD `.forge/skills/` > Agent > Global > Built-in。

### Layer 4: 基础设施 (`forge_infra`)

文件 I/O、Shell 执行、HTTP Client（proxy、TLS、重试）、进程管理。

### Layer 5: 入口点 (`forge_main`)

CLI 参数解析 → 加载配置 → 初始化 provider → 创建 Agent + Conversation → 启动 TUI → Orchestrator.run()

---

## 二、OpenCode 架构（6 层）

### Layer 0: 标识符 + Schema

```typescript
// Effect-TS Schema：编译时类型安全 + 运行时验证
const SessionID = Schema.String.pipe(Schema.brand("SessionID"))
const MessageID = Schema.String.pipe(Schema.brand("MessageID"))
const PartID = Schema.Number.pipe(Schema.brand("PartID"))
```

Agent 定义：
```typescript
const Info = Schema.Struct({
  name: Schema.String,
  mode: Schema.Literals(["subagent", "primary", "all"]),
  permission: Permission.Ruleset,  // 每个 agent 独立权限
  model: { modelID, providerID },
  prompt: Schema.String,
  steps: Schema.Finite,            // subagent 硬限制
})
```

### Layer 1: 持久化（SQLite）

OpenCode 独有的精细度——message 拆成 part 级别：

```
Session → Message[] → Part[]
  Part types:
    TextPart      (text + time + metadata)
    ToolPart      (tool name + callID + state {pending|running|completed|error})
    ReasoningPart (reasoning text + time)
    StepStartPart (snapshot hash)
    StepFinishPart(finish reason + tokens + cost + patch)
    PatchPart     (file diffs)
```

每个 text-delta、tool call、reasoning chunk 都是独立 DB 行。这意味着：
- UI 增量渲染（每个 delta 独立到达）
- 任意 part 边界 fork 对话
- Compaction 按 part 粒度修剪
- 每次 step 的文件变更精确归因

### Layer 2: Core Services（Effect-TS Layer）

```typescript
Config.Service  → get(): Effect<Config>           // 读配置
Provider.Service → getModel(id): Effect<Model>     // 查模型
Agent.Service   → get(name): Effect<Agent.Info>    // 查 agent
Permission.Service → ask(...): Effect<"allow"|"deny">  // 权限
Plugin.Service  → trigger(hook, data): Effect<data>    // 插件钩子
```

DI 通过 Effect-TS 的 `Layer` + `yield*` 编译时检查依赖完整性。

### Layer 3: Tool System

每个工具是独立模块：
```typescript
const ReadTool = {
    definition: { name, description, parameters: z.object({...}) },
    execute: async (params, context) => { ... }
}
```

工具注册在 `ToolRegistry`：
```typescript
builtin: [ReadTool, WriteTool, ShellTool, GrepTool, GlobTool,
          EditTool, TaskTool, SkillTool, WebSearchTool, WebFetchTool,
          LspTool, PlanTool, QuestionTool, TodoWriteTool, ...]
```

### Layer 4: Session Processor（核心事件 loop）

```typescript
process(streamInput): Effect<"continue" | "compact" | "stop"> {
    stream = llm.stream(streamInput);  // Vercel AI SDK 流
    stream.pipe(
        Stream.tap(handleEvent),       // 事件分发
        Stream.takeUntil(needsCompaction),
        Stream.runDrain,
    );
    // 返回决策给外层
}
```

handleEvent 分发：
```
"text-start/delta/end" → 创建/更新/完成 TextPart
"tool-input-start"     → 创建 ToolPart (pending)
"tool-call"           → 执行工具 + doom loop 检测
"tool-result"         → 完成 ToolPart
"tool-error"          → 失败处理 + blocked 检查
"reasoning-start/delta/end" → 创建/更新 ReasoningPart
"start-step"          → 捕获 snapshot
"finish-step"         → 生成 patch + token 用量 + overflow 检测
```

外层调用者在 loop 中调用 process，根据返回值决定 compact/stop/continue。

### Layer 5: Session 管理

```typescript
Session.create({ title, agent, model }) → 创建 session
Session.fork({ sessionID, messageID })  → message 级 fork
Session.messages({ sessionID })         → 读取所有 message + parts
```

支持 ACP 协议（Agent Client Protocol），标准化了 NewSession/LoadSession/ForkSession/Prompt/Cancel。

### Layer 6: 入口点

CLI → ACP Server → TUI / Desktop (Electron) / VS Code Extension / Web UI

---

## 三、对比总结

| 维度 | ForgeCode | OpenCode |
|------|-----------|----------|
| **语言** | Rust | TypeScript (Bun + Effect-TS) |
| **第 0 层** | Struct/enum（编译时） | Schema（编译+运行时验证） |
| **Agent 定义** | `Agent { tools, model, prompt }` 纯数据 | `Agent.Info { mode, permission, steps }` Schema |
| **持久化粒度** | Conversation（message 级） | Session → Message → **Part**（独立行） |
| **核心 loop** | `while !should_yield` 状态机 | Stream 事件驱动 + Effect 组合 |
| **工具派发** | 3 级：ToolCatalog → AgentExecutor → MCP | 统一 ToolRegistry → execute() |
| **权限** | PolicyEngine（Allow/Deny/Confirm + rule） | Permission ruleset per agent + doom_loop |
| **Hook** | 6 事件 + .zip()/.and() + End 可重入 | Effect Layer + Plugin trigger |
| **子 agent** | 内置 3 agent + Task 工具 | primary/subagent mode + ACP |
| **Compaction** | token_threshold + percentage | overflow 检测 + 结构化摘要 |
| **Session 操作** | new/resume/clone/dump | create/fork/resume + message 级 fork |

---

## 四、共同设计模式（6 条铁律）

### 1. Agent = 数据 + prompt + 工具白名单
新 agent 行为 = 填配置，不写代码。行为由 model × system_prompt × tools 决定。

### 2. 核心 loop 极简，复杂度外挂
`while true` 是核心。所有扩展通过 hook/transform/plugin/wrapper 层完成，不动核心 loop。

### 3. 工具描述动态生成
根据当前模型能力渲染工具描述。不支持 image 的模型看到的 Read 描述和不支持的不同。Handlebars 模板按 model capabilities 动态渲染。

### 4. 上下文是受限资源
三级渐进披露（元数据 → 正文 → 资源），按需加载。每 token 都要钱，精确管理谁看到什么、什么时候看到。

### 5. Agent 间用文件通信
子 agent 回传结构化结果，不共享上下文窗口。Coordinator 被剥夺文件访问权（CC 的设计），只路由、不执行。

### 6. "我完成了"永远不可信
Gate 必须是机械化外部检查（文件存在？frontmatter 完整？数值一致？），永远不能用 LLM 自评。

---

## 五、对物理 Agent 的启示

1. **物理 agent 的大脑应该是 prompt 工程 + 知识层，不是代码逻辑。** 从 Forge 学到：agent 行为 = system_prompt 模板 + custom_rules + 工具白名单。

2. **物理思维追问应该注入到 Transform pipeline。** 每次 LLM 调用前，transform 层注入 4 个强制追问（物理本质/知识关联/信息缺口/完成标准）。不是新 gate，是 agent 内部 deliberation 引导。

3. **Retreat checkpoint 用 OpenCode 的 Part 级状态模型。** 不只是 "当前在 L3"，而是精确到 subplane + activity + partial_state。Retreat 时保存，return 时恢复。

4. **Gate 是机械化检查组件。** 可复用的独立模块：文件存在检查、frontmatter 字段完整性、数值一致性校验。不用 LLM。

5. **成长机制 = 每次失败 → rule → AGENTS.md。** Anthropic 的元原则：harness engineering is accumulation。每次 agent 犯错，写一条 rule，永不重复。
