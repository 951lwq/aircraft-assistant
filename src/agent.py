"""
LangChain Agent：自动路由用户问题到正确的工具，支持多轮对话记忆。

Agent 根据用户问题自动判断调用哪个工具，并记住之前的对话上下文，
能够理解"它"、"其中"、"刚才"等指代。

工具列表：
- rag_knowledge_base  → 概念/流程/定义类问题
- aircraft_database    → 飞机状态/数据查询
- rent_calculator      → 租金动态计算

使用 LangChain create_tool_calling_agent + AgentExecutor 模式。
"""

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.config import config
from src.tools import get_all_tools


# ─── System Prompt ────────────────────────────────────────

SYSTEM_PROMPT = """你是一个飞机资产管理智能助手，支持多轮对话。你拥有以下专业工具：

【知识库】
- **rag_knowledge_base**：查概念/流程/定义。如"什么是融资租赁""退租检查流程"。

【单字段精准查询】（用户只问一个维度时使用，回答会自动精简）
- **get_aircraft_status**：只查租赁状态。如"B-3201 的状态？"
- **get_aircraft_lease_type**：只查租赁方式（融资/经营）。如"B-7378 是融资租赁吗？"
- **get_aircraft_rental_price**：只查租金单价+计算方式+市场费率。如"B-7879 的租金？"
- **get_aircraft_model**：只查机型。如"B-3509 什么型号？"
- **get_aircraft_lessee_lessor**：只查承租方+出租方。如"B-3201 哪家航空公司的？"

【批量/全量查询】
- **search_aircraft**：按条件批量搜索。如"A320 有哪些""在租的飞机""东方航空的飞机"。
- **get_fleet_statistics**：全量统计概览。如"机队整体情况""各状态分布"。
- **get_aircraft_full_info**：全部字段。仅当用户明确要"详细信息""完整信息"时使用。

【计算】
- **rent_calculator**：动态计算租金（需要乘法）。如"B-7378 飞 240 小时多少钱？"
  如果用户只查单价不计算，用 get_aircraft_rental_price，不要用本工具。

**核心规则（必须遵守）：**
1. **按需选工具**：用户问什么就选对应工具。问状态 → get_aircraft_status，
   问租金 → get_aircraft_rental_price，问机型 → get_aircraft_model。
   不要因为方便就用 search_aircraft 或 get_aircraft_full_info 代替单一工具。
2. **回答精简**：工具返回什么就说什么，不要补充无关字段。用户问状态就只说状态。
3. **禁止篡改数据（极其重要）**：工具返回的注册号、机型号、承租方、出租方、金额
   等具体数据，必须原样引用，绝对不允许修改、替换、或编造。即使工具返回的
   数据看起来与你记忆中的不一致，也必须以工具返回为准。
4. 概念问题用 rag_knowledge_base，数据查询用对应数据工具。
5. **记忆上下文**：理解"它""其中""刚才""那"等指代词。
6. 中文回答。
7. **输出格式**：纯文本，不使用 Markdown 标记。禁止使用 ** 加粗、禁止 |---| 表格。
   列表项直接用缩进对齐即可。"""


# ─── Agent 构建 ───────────────────────────────────────────

def build_agent() -> AgentExecutor:
    """
    创建并返回 AgentExecutor（无状态，每次调用独立）。

    使用 create_tool_calling_agent 模式：
    1. LLM 根据 system prompt + 工具描述决定调用哪个工具
    2. 工具执行后结果返回给 LLM
    3. LLM 综合生成最终回答

    多轮对话记忆由 cli_agent 通过 chat_history 参数实现。
    """
    config.validate()

    # 1. LLM
    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        openai_api_key=config.DEEPSEEK_API_KEY,
        openai_api_base=config.DEEPSEEK_BASE_URL,
        temperature=0.3,
        max_tokens=1024,
    )

    # 2. 工具列表
    tools = get_all_tools()

    # 3. Prompt 模板（含 chat_history 占位符，支持多轮对话）
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # 4. 创建 Agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    # 5. 包装为 Executor
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=5,
    )

    return executor
