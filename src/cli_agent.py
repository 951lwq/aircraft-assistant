"""
命令行交互式 Agent 问答脚本（支持多轮对话记忆）。
集成 RAG 知识库 + 飞机数据库 + 租金计算器，Agent 自动判断调用哪个工具。

对话记忆：Agent 会记住之前的对话内容，能理解"它"、"其中"、"刚才"等指代。

启动后进入对话循环：
- 概念性问题  → 知识库（RAG）
- 数据查询    → 飞机数据库
- 租金计算    → 租金计算器
- 输入 quit   → 退出
- 输入 /clear → 清除对话记忆

用法:
    python -m src.cli_agent          # 标准模式
    python -m src.cli_agent -v       # 详细模式（显示 Agent 推理过程）
"""

import os as _os
_os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

import sys
import textwrap

# 修复 Windows 终端编码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")

from langchain_core.messages import HumanMessage, AIMessage

from src.config import config
from src.agent import build_agent


# ─── 命令行界面 ───────────────────────────────────────────

def print_banner():
    print("=" * 64)
    print("  飞机资产管理智能助手  v2.0")
    print("  工具：知识库(RAG) | 飞机数据库 | 租金计算器")
    print("  支持多轮对话记忆 | /clear 清除记忆 | quit 退出")
    print("=" * 64)
    print()


def print_result(question: str, answer: str) -> None:
    """格式化打印结果。"""
    print("-" * 64)
    print(f"[A]")
    # 不 textwrap，保留表格原始格式
    print(answer)
    print("-" * 64 + "\n")


def main():
    """交互式 Agent 主循环（带对话记忆）。"""
    verbose = "-v" in sys.argv or "--verbose" in sys.argv

    # 检查配置
    try:
        config.validate()
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    # 构建 Agent
    print(">>> Initializing Agent...")
    try:
        agent = build_agent()
        if verbose:
            agent.verbose = True
    except Exception as e:
        print(f"[ERROR] Agent build failed: {e}")
        sys.exit(1)

    print_banner()

    # ── 对话记忆（消息列表）──
    chat_history: list = []

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not question:
            continue

        # 特殊命令
        if question.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break

        if question == "/clear":
            chat_history.clear()
            print("[Memory cleared]\n")
            continue

        # 调用 Agent（传入历史消息）
        try:
            result = agent.invoke({
                "input": question,
                "chat_history": chat_history,
            })
            answer = result.get("output", str(result))

            # 存入记忆
            chat_history.append(HumanMessage(content=question))
            chat_history.append(AIMessage(content=answer))

            if verbose:
                print(f"\n[DEBUG] chat_history length: {len(chat_history)}")

            print_result(question, answer)

        except Exception as e:
            print(f"[ERROR] {e}\n")


if __name__ == "__main__":
    main()
