"""
Streamlit Web 前端 — 飞机资产管理智能助手。

提供 ChatGPT 风格的对话界面，集成 RAG 知识库 + 飞机数据库 + 租金计算器。
Agent 自动判断用户意图并路由到正确的工具。

启动方式:
    streamlit run src/app.py

依赖:
    streamlit>=1.28
"""

import os as _os
_os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
_os.environ.setdefault("CHROMA_ANONYMIZED_TELEMETRY", "False")

import sys as _sys

# 将项目根目录加入 sys.path，确保 streamlit run src/app.py 能导入 src 包
_project_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _project_root not in _sys.path:
    _sys.path.insert(0, _project_root)

import streamlit as st

from langchain_core.messages import HumanMessage, AIMessage

from src.config import config
from src.agent import build_agent
from src.tools import get_all_tools


# ══════════════════════════════════════════════════════════════
# 页面配置
# ══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="飞机资产管理智能助手",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ══════════════════════════════════════════════════════════════
# Agent 缓存（只初始化一次，避免重复加载模型和向量库）
# ══════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def get_agent():
    """加载并返回 AgentExecutor。使用 Streamlit 缓存避免重复初始化。"""
    config.validate()
    return build_agent()


# ══════════════════════════════════════════════════════════════
# Session State 初始化
# ══════════════════════════════════════════════════════════════

def init_session_state():
    """初始化会话状态变量。"""
    if "chat_history" not in st.session_state:
        # LangChain 消息列表（传给 agent.invoke）
        st.session_state.chat_history = []

    if "messages" not in st.session_state:
        # 展示用消息列表
        st.session_state.messages = []

    if "agent_ready" not in st.session_state:
        st.session_state.agent_ready = False


init_session_state()


# ══════════════════════════════════════════════════════════════
# 侧边栏
# ══════════════════════════════════════════════════════════════

def render_sidebar():
    """渲染侧边栏：工具列表、示例问题、操作按钮。"""
    with st.sidebar:
        st.title("✈️ 飞机资产管理助手")
        st.caption("v2.0 — RAG + Agent")

        # ── 状态指示 ──
        if st.session_state.agent_ready:
            st.success("Agent 已就绪")
        else:
            st.warning("Agent 初始化中...")

        st.divider()

        # ── 功能说明 ──
        st.subheader("功能")
        st.markdown("""
        - **知识库问答** — 租赁方式、管理流程、退租检查等
        - **飞机数据查询** — 状态、机型、租金、承租方/出租方
        - **批量搜索** — 按机型/状态/航空公司筛选
        - **租金计算** — 按小时/月/年动态计算
        - **机队统计** — 整体分布概览
        """)

        st.divider()

        # ── 可用工具列表 ──
        st.subheader("Agent 工具")
        tools = get_all_tools()
        for tool in tools:
            with st.expander(tool.name):
                desc = tool.description.split("\n")[0] if tool.description else "无描述"
                st.caption(desc)

        st.divider()

        # ── 操作按钮 ──
        if st.button("清除对话记忆", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.messages = []
            st.rerun()

        st.divider()

        # ── 示例问题 ──
        st.subheader("示例问题")
        examples = [
            "什么是经营租赁？",
            "B-3201 的状态是什么？",
            "B-7378 的租金怎么算？",
            "A320 的飞机有哪些？",
            "工银金融租赁的飞机有哪些？",
            "B-7378 飞了 240 小时总租金多少？",
            "机队整体统计情况",
            "B-3509 是哪家航空公司的？",
        ]
        for q in examples:
            if st.button(q, use_container_width=True):
                # 将示例问题填入输入并触发
                st.session_state.pending_question = q
                st.rerun()


# ══════════════════════════════════════════════════════════════
# 主界面
# ══════════════════════════════════════════════════════════════

def main():
    """主界面：对话区域 + 输入框。"""

    # ── 页面标题 ──
    st.title("飞机资产管理智能助手")
    st.caption("基于 RAG + Agent 架构 | 知识库 + 飞机数据库 + 租金计算器 | 多轮对话记忆")

    st.divider()

    # ── 初始化 Agent ──
    if not st.session_state.agent_ready:
        with st.spinner("正在初始化 Agent，加载模型和向量库..."):
            try:
                agent = get_agent()
                st.session_state.agent_ready = True
            except Exception as e:
                st.error(f"Agent 初始化失败: {e}")
                st.info("请检查：\n1. .env 文件中的 DEEPSEEK_API_KEY 是否配置\n2. 是否已运行 python -m src.ingest 摄入文档")
                return
    else:
        agent = get_agent()

    # ── 渲染历史消息 ──
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── 输入框（始终渲染，否则点击示例问题后输入框会消失）──
    user_input = st.chat_input("输入你的问题...")

    # 侧边栏示例问题优先于手动输入
    if "pending_question" in st.session_state:
        question = st.session_state.pending_question
        del st.session_state.pending_question
    else:
        question = user_input

    if not question:
        return

    # ── 显示用户消息 ──
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # ── 调用 Agent ──
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                result = agent.invoke({
                    "input": question,
                    "chat_history": st.session_state.chat_history,
                })
                answer = result.get("output", str(result))
            except Exception as e:
                answer = f"抱歉，处理请求时出错：{e}"

        st.markdown(answer)

    # ── 存入对话记忆 ──
    st.session_state.chat_history.append(HumanMessage(content=question))
    st.session_state.chat_history.append(AIMessage(content=answer))
    st.session_state.messages.append({"role": "assistant", "content": answer})


# ══════════════════════════════════════════════════════════════
# 入口
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    render_sidebar()
    main()
