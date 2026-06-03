"""
命令行交互式问答脚本。
启动后进入对话循环，输入问题获取回答，输入 quit 退出。
"""

import os as _os
_os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

import sys
import textwrap


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")

from src.config import config
from src.retriever import build_qa_chain


def print_answer(question: str, result: dict) -> None:
    """格式化打印问答结果。"""
    print("\n" + "=" * 60)
    print(f"[Q] {question}")
    print("-" * 60)
    print(f"[A]\n{textwrap.fill(result['result'], width=56)}")
    print("-" * 60)

    # 打印来源文档
    sources = result.get("source_documents", [])
    if sources:
        print("[Sources]")
        shown = set()
        for doc in sources:
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page")
            if page:
                source_key = f"{source} (Page {page})"
            else:
                source_key = source

            if source_key not in shown:
                print(f"   * {source_key}")
                shown.add(source_key)

    print("=" * 60 + "\n")


def main():
    """交互式问答主循环。"""
    # 检查配置
    try:
        config.validate()
    except ValueError as e:
        print(f"[ERROR] Config error: {e}")
        print("  Please copy .env.example to .env and fill in your API Key")
        sys.exit(1)

    # 构建 QA 链
    print(">>> Initializing Aircraft Asset Management Knowledge Assistant...")
    try:
        qa_chain = build_qa_chain()
    except Exception as e:
        print(f"[ERROR] Init failed: {e}")
        print("  Hint: run 'python -m src.ingest' first to ingest documents")
        sys.exit(1)

    print(">>> Ready! Type your question, or 'quit' to exit.\n")

    # 对话循环
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q", "退出"):
            print("Bye!")
            break

        # 调用 QA 链
        try:
            result = qa_chain.invoke({"query": question})
            print_answer(question, result)
        except Exception as e:
            print(f"[ERROR] Query failed: {e}\n")


if __name__ == "__main__":
    main()
