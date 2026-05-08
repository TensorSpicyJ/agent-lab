"""
01-minimal-harness — 最小的可跑 agent harness
=============================================
Agent = LLM 做决策
Harness = 验证限制记录恢复

跑法: python agent.py "在 D:\playground\agent-lab\experiments\01-minimal-harness 下建一个 hello.txt，内容是 hello world"
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from openai import OpenAI

# ═══════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════
MODEL = "deepseek-chat"
BASE_URL = "https://api.deepseek.com"
SANDBOX_DIR = Path(__file__).parent  # agent 只能在当前目录操作

client = OpenAI(base_url=BASE_URL, api_key=os.environ["DEEPSEEK_API_KEY"])


# ═══════════════════════════════════════════════════
# 工具定义 (Agent 的"手")
# ═══════════════════════════════════════════════════
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read content of a file",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run a shell command. Use sparingly.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
]


# ═══════════════════════════════════════════════════
# Harness: 工具执行 + 安全检查
# ═══════════════════════════════════════════════════
def resolve_path(path: str) -> Path:
    """所有路径相对于 SANDBOX_DIR。禁止 ../ 逃逸。"""
    p = (SANDBOX_DIR / path).resolve()
    if SANDBOX_DIR not in p.parents and p != SANDBOX_DIR.resolve():
        raise PermissionError(f"Path escapes sandbox: {path}")
    return p


def execute_tool(name: str, args: dict) -> str:
    """执行工具调用，返回结果字符串。这里是 harness 第一道门。"""
    try:
        if name == "read_file":
            p = resolve_path(args["path"])
            if not p.exists():
                return f"Error: file not found: {p}"
            return p.read_text(encoding="utf-8")

        elif name == "write_file":
            p = resolve_path(args["path"])
            p.parent.mkdir(parents=True, exist_ok=True)
            before = p.read_text(encoding="utf-8") if p.exists() else None
            p.write_text(args["content"], encoding="utf-8")
            # Gate: 写完后验证实际写入了
            after = p.read_text(encoding="utf-8")
            if after != args["content"]:
                return f"Error: write verification failed — file content mismatch"
            return f"Written: {p} ({len(after)} bytes)"

        elif name == "run_shell":
            cmd = args["command"]
            # Gate: 禁止危险命令
            dangerous = ["rm -rf", "format", "del /f", "shutdown", "> /dev/"]
            for d in dangerous:
                if d.lower() in cmd.lower():
                    return f"DENIED: dangerous command pattern '{d}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=str(SANDBOX_DIR))
            return result.stdout + result.stderr

        elif name == "list_dir":
            p = resolve_path(args["path"])
            if not p.exists():
                return f"Error: directory not found: {p}"
            return "\n".join(str(x.relative_to(p)) for x in p.iterdir())

        else:
            return f"Unknown tool: {name}"

    except PermissionError as e:
        return f"DENIED: {e}"
    except Exception as e:
        return f"Error executing {name}: {e}"


# ═══════════════════════════════════════════════════
# System Prompt (Agent 的行为约束)
# ═══════════════════════════════════════════════════
SYSTEM_PROMPT = f"""You are a coding agent. You have tools to read/write files and run shell commands.

Rules:
- ALL file paths are relative to {SANDBOX_DIR}
- After you make changes, verify them by reading the file back
- When done, say "DONE" and summarize what you did
- If you can't complete the task, say "BLOCKED" and explain why
- Be concise
"""


# ═══════════════════════════════════════════════════
# Agent Loop (最简 while True)
# ═══════════════════════════════════════════════════
def run(task: str, max_turns: int = 15) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    log = []  # trace
    final_status = "UNKNOWN"

    for turn in range(1, max_turns + 1):
        print(f"\n--- Turn {turn} ---")

        # LLM 调用
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            temperature=0.2,
        )
        msg = resp.choices[0].message

        # Agent 说了什么
        if msg.content:
            print(f"[Agent]: {msg.content[:300]}")

        # 没有工具调用 → agent 认为完成了
        if not msg.tool_calls:
            content = msg.content or ""
            if "DONE" in content:
                final_status = "DONE"
            elif "BLOCKED" in content:
                final_status = "BLOCKED"
            else:
                final_status = "FINISHED_NO_DONE"
            messages.append({"role": "assistant", "content": content})
            break

        # 执行工具
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ],
        })

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            print(f"[Tool]: {tc.function.name}({json.dumps(args, ensure_ascii=False)[:100]})")
            result = execute_tool(tc.function.name, args)
            print(f"[Result]: {result[:200]}")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })
            log.append({"turn": turn, "tool": tc.function.name, "args": args, "result": result[:200]})

    # ════════════════════════════════════════════
    # HARSH Gate: agent 说自己完成了，真完成了吗？
    # ════════════════════════════════════════════
    verification = verify_task(task, log)

    return {
        "task": task,
        "status": final_status,
        "turns": turn,
        "verification": verification,
        "log": log,
    }


# ═══════════════════════════════════════════════════
# Harness Gate: 事后验证（不问 agent，自己查）
# ═══════════════════════════════════════════════════
def verify_task(task: str, log: list) -> dict:
    """Harness 层面验证 agent 是否真的完成了任务。这是第二道门。"""
    checks = {}

    # Check 1: agent 有没有写入东西？
    writes = [e for e in log if e["tool"] == "write_file"]
    checks["made_changes"] = len(writes) > 0

    # Check 2: 写了之后验证了没有？
    reads_after_write = False
    for i, e in enumerate(log):
        if e["tool"] == "write_file" and i + 1 < len(log):
            if log[i + 1]["tool"] == "read_file":
                reads_after_write = True
                break
    checks["verified_own_work"] = reads_after_write

    # Check 3: 有没有被拒绝的操作？
    denied = [e for e in log if "DENIED" in str(e["result"])]
    checks["had_denials"] = len(denied) > 0

    checks["verdict"] = "PASS" if checks["made_changes"] else "SUSPECT: no writes detected"

    return checks


# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "在 sandbox 下建 hello.txt，内容 hello world"
    print(f"{'='*60}")
    print(f"Task: {task}")
    print(f"Sandbox: {SANDBOX_DIR}")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"{'='*60}")

    result = run(task)

    print(f"\n{'='*60}")
    print(f"Status: {result['status']} | Turns: {result['turns']}")
    print(f"Verification: {json.dumps(result['verification'], ensure_ascii=False)}")
    print(f"{'='*60}")
