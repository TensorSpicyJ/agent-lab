# 怎么写 Agent 和 Harness — 从理念到 Vibe Coding

## 先分清两个东西

```
Agent  = 做决策的东西（"我要读这个文件、搜那个、然后写到这里"）
Harness = 管住 agent 的东西（"你做了决定，但我来验证、限制、记录、恢复"）
```

**一句话：Agent 是大脑，Harness 是脑壳+免疫系统+神经系统。**

CC 泄露源码印证了这一点——模型调用代码只占 1.6%（~8000 行），剩下 98.4% 全是 harness：工具派发、权限检查、上下文压缩、hook 触发、子 agent 协调、记忆管理、遥测。

## 核心理念（五源汇聚后的最小共识）

### 1. Agent 的"我完成了"永远不可信

这是门槛级教训。所有五个来源都反复验证：agent 会自欺。

怎么解决？**机械化 gate。** 不是 prompt 说"请确认完成"，而是代码检查：
- AITP 方式：文件存在吗？frontmatter 字段全吗？标题对得上吗？
- Superpowers 方式：先看测试失败，再写代码，再看通过——不跳过任何一步
- CC 方式：工具执行前必须经过 validateInput() → checkPermissions()，两层检查失败直接拒绝

**你写的时候：** 别问 agent "你确定吗"，写个函数检查"agent 声称改了 3 个文件，这三个文件真的被修改了吗，git diff 有内容吗"。

### 2. 每次 agent 犯错，变成一个 rule

这是 Anthropic 团队的元原则，也是 superpowers 最值钱的部分。

```
Agent 犯了错
  → 写一个 hook/rule/skill 防止再犯
  → 这个规则成为 harness 的永久部分
  → 重复 100 次后，你的 harness 就是制度性知识
```

**你写的时候：** 第一次让 agent 随便跑。它搞砸了。你别修 bug，你修 harness。下次它就不可能犯同样的错。

### 3. 上下文是钱

每 token 都要钱。Progressive disclosure（渐进披露）是所有五个来源的共同模式：

| 层级 | 加载时机 | 大小 |
|------|----------|------|
| 元数据 | 始终在上下文 | ~100 words |
| 技能正文 | 触发时加载 | <5000 words |
| 参考资料 | 显式按需 | 不限 |

**你写的时候：** 别把所有技能/规则/背景塞 system prompt。用两级索引——先让 agent 看到"有这个能力"，它说需要时再加载细节。

### 4. Agent 之间用文件通信，不共享上下文

这是 CC 泄露最反直觉的设计：**Coordinator 被剥夺了直接文件访问权。** 它只能路由消息、派发 worker。Worker 们也互不共享上下文窗口。

**你写的时候：** 主 agent 读 plan.md → 拆成 task → 派给子 agent（只给 task 自身需要的上下文）→ 子 agent 写入结果文件 → 主 agent 读结果文件 → 汇总。每一步都是文件交接，不是内存传递。

### 5. Hook 是架构，不是功能

CC 有 25+ 生命周期事件，Forge 用 `.zip()` `.and()` 组合 hook。核心 loop 都是 `while true` ——极简。所有复杂度在 hook/wrapper 层。

**你写的时候：** 先写最简单的 loop：`while True: ask_llm() → execute_tools() → append_results() → repeat`。然后每个新需求都作为 hook 挂上去，不动核心 loop。

## Vibe Coding Harness 的方法

"Vibe coding" 不是瞎写，是**先让 agent 裸跑 → 看失败模式 → 加约束 → 重复**。区别是你代码的对象是 agent，不是你。

### 第一轮：裸跑

```python
# 最简单的 harness —— 不到 30 行
while True:
    response = llm.chat(messages)
    if response.has_tool_calls():
        for tool in response.tool_calls:
            result = execute(tool)  # 不做任何检查
            messages.append(result)
    else:
        break
```

让 agent 在真实任务上跑。它会：读不该读的文件、删重要东西、陷入死循环、声称完成了但什么都没改、编造不存在的 API。

**这些失败是你 harness 的需求文档。** 每个失败告诉你："这里需要一个 gate。"

### 第二轮：加门控

agent 说"完成了" → 检查实际上做了什么：

```python
if response.is_final():
    changed = git_diff()  # 检查实际文件变更
    if not changed:
        messages.append("你说完成了但没有修改任何文件。请确认。")
        continue
    if spec_check(changed):  # 对照 spec 逐条检查
        break
```

### 第三轮：加权限

```python
def execute(tool):
    if tool.type == "shell" and "rm -rf" in tool.command:
        return "DENIED: destructive operations require explicit confirmation"
    if tool.type == "write" and is_protected(tool.path):
        return "DENIED: this file is in protected zone"
    return tool.execute()
```

### 第四轮：加恢复

agent 卡住了、死循环了、连续失败 → 不需要你手动干预：

```python
if consecutive_failures > 3:
    messages.append(f"你已经失败了 {consecutive_failures} 次。请停下来分析根因，不要重试同样的事情。")
    if consecutive_failures > 5:
        yield_to_human()  # 或者回退到上一个 checkpoint
```

### 第五轮：加记忆

```python
# L1: 跨会话持久
memory = read("AGENTS.md")  # 从上次 session 学到的东西

# L2: 会话内检索
relevant_code = grep(codebase, current_task_keywords)

# L3: 后台巩固（以后做）
# autoDream: 过期的记忆自动清理
```

### 一直迭代

每跑一次，观察失败，加一条规则。三个月后你的 harness 就有 100 条规则，每条对应一个真实踩过的坑。这就是 Anthropic 说"harness engineering is accumulation"的意思。

## 现在就开始

你不需要先建 19 个 crate 或写 51 万行。最小可跑 harness：

1. 一个 LLM 调用（DeepSeek API）
2. 几个工具（读文件、写文件、搜代码、跑 shell）
3. 一个 while loop
4. 一个门控（"你说完成了，我真的检查一下"）

**先让它在真实任务上跑砸，然后修 harness，不修 bug。** 这就是 vibe coding 的 harness 写法。
