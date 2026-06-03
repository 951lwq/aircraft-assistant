"""
LangChain 工具定义（按需查询，精简回答）。

工具清单（共 9 个）：
  数据查询（按字段拆分）：
    1. get_aircraft_status      — 仅返回租赁状态
    2. get_aircraft_lease_type  — 仅返回租赁方式
    3. get_aircraft_rental_price— 仅返回租金单价+计算方式+市场费率
    4. get_aircraft_model       — 仅返回机型
    5. get_aircraft_lessee_lessor — 返回承租方+出租方
    6. get_aircraft_full_info   — 全量信息（用户明确要"全部/详细"时用）
    7. search_aircraft          — 按条件批量搜索（机型/状态/航空公司等）
    8. get_fleet_statistics     — 全量统计概览
  知识 + 计算（保留）：
    9. rag_knowledge_base
   10. rent_calculator
"""

from typing import Optional

from langchain_core.tools import tool

from src.retriever import build_qa_chain
from src.data.aircraft_data import (
    get_aircraft_df,
    lookup_status,
    lookup_lease_type,
    lookup_rental_price,
    lookup_model,
    lookup_lessee_lessor,
    lookup_full_info,
    search_fleet,
    fleet_statistics,
    calculate_rent,
    calculate_all_hourly_rates,
)


# ─── 全局缓存 ──────────────────────────────────────────────

_qa_chain_cache: Optional[object] = None


def _get_qa_chain():
    global _qa_chain_cache
    if _qa_chain_cache is None:
        _qa_chain_cache = build_qa_chain()
    return _qa_chain_cache


# ═══════════════════════════════════════════════════════════
#  知识库工具（保留不变）
# ═══════════════════════════════════════════════════════════

@tool
def rag_knowledge_base(question: str) -> str:
    """
    查询飞机资产管理知识库，获取概念性、流程性、定义类知识。

    适用场景：
    - "什么是融资租赁/经营租赁？"
    - "飞机资产管理的三个阶段是什么？"
    - "LLP 寿命限制件的监控规则是什么？"
    - "退租检查包含哪些内容？"
    - "维修储备金的费率如何计算？"
    - "融资租赁和经营租赁有什么区别？"

    参数:
        question: 知识性问题
    返回:
        基于知识库文档的回答
    """
    qa = _get_qa_chain()
    result = qa.invoke({"query": question})
    return result["result"]


# ═══════════════════════════════════════════════════════════
#  飞机数据工具（按字段拆分，精简返回）
# ═══════════════════════════════════════════════════════════

@tool
def get_aircraft_status(reg_no: str) -> str:
    """
    查询某架飞机的当前租赁状态。仅返回状态信息（在租/维修中/退租中/待交付），
    不返回其他字段。

    适用场景：
    - "B-3201 的状态是什么？"
    - "B-3202 现在在租吗？"
    - "查一下 B-7375 的状态"

    参数:
        reg_no: 飞机注册号，如 "B-3201"
    返回:
        精简的状态信息
    """
    return lookup_status(reg_no)


@tool
def get_aircraft_lease_type(reg_no: str) -> str:
    """
    查询某架飞机的租赁方式。仅返回租赁方式（融资租赁 或 经营租赁），
    不返回其他字段。

    适用场景：
    - "B-7378 是融资租赁还是经营租赁？"
    - "B-3302 的租赁方式是什么？"

    参数:
        reg_no: 飞机注册号，如 "B-7378"
    返回:
        精简的租赁方式信息
    """
    return lookup_lease_type(reg_no)


@tool
def get_aircraft_rental_price(reg_no: str) -> str:
    """
    查询某架飞机的租金单价、计算方式和市场费率参考。仅返回价格相关信息，
    不返回状态、承租方等无关字段。

    适用场景：
    - "B-3201 的租金是多少？"
    - "B-7879 的租金单价？"
    - "B-7378 按小时怎么收费？"

    注意：如果用户要求计算具体金额（如"飞了 240 小时总租金多少"），
    请使用 rent_calculator 工具，而不是本工具。

    参数:
        reg_no: 飞机注册号，如 "B-7879"
    返回:
        精简的租金信息（单价 + 计算方式 + 市场费率）
    """
    return lookup_rental_price(reg_no)


@tool
def get_aircraft_model(reg_no: str) -> str:
    """
    查询某架飞机的机型号。仅返回机型，不返回其他字段。

    适用场景：
    - "B-3205 是什么机型？"
    - "B-3509 的型号？"

    参数:
        reg_no: 飞机注册号，如 "B-3509"
    返回:
        精简的机型信息
    """
    return lookup_model(reg_no)


@tool
def get_aircraft_lessee_lessor(reg_no: str) -> str:
    """
    查询某架飞机的承租方和出租方。仅返回航空公司与租赁公司信息。

    适用场景：
    - "B-3201 是哪家航空公司的？"
    - "B-7378 的出租方是谁？"
    - "B-7879 谁在租？哪个公司出租的？"

    参数:
        reg_no: 飞机注册号，如 "B-3201"
    返回:
        精简的承租方+出租方信息
    """
    return lookup_lessee_lessor(reg_no)


@tool
def get_aircraft_full_info(reg_no: str) -> str:
    """
    查询某架飞机的全部信息（所有字段）。
    仅在用户明确要求"详细信息"、"完整信息"、"全部信息"时使用，
    或用户同时问了多个不同维度的字段时使用。

    适用场景：
    - "B-3201 的详细信息"
    - "把 B-7378 的所有信息都列出来"

    注意：如果用户只问单一维度（如只问状态、只问租金），
    请用对应的单一工具，不要使用本工具。

    参数:
        reg_no: 飞机注册号，如 "B-3201"
    返回:
        全量字段信息
    """
    return lookup_full_info(reg_no)


@tool
def search_aircraft(query: str) -> str:
    """
    按条件批量搜索飞机。支持按机型、租赁状态、航空公司、租赁方式、
    出租方等维度筛选。返回匹配飞机的关键字段表格。

    适用场景：
    - "A320 的飞机有哪些？"
    - "在租的飞机有哪些？"
    - "东方航空承租了哪几架？"
    - "经营租赁的飞机有哪些？"
    - "工银金融租赁出租了哪些飞机？"
    - "维修中的飞机"

    不适用场景：
    - 查询单架飞机的某个具体字段（请用对应的单一工具）
    - 概念性问题（请用 rag_knowledge_base）

    参数:
        query: 搜索条件描述，如机型、状态、航空公司名
    返回:
        Markdown 表格格式的匹配飞机列表
    """
    return search_fleet(query)


@tool
def get_fleet_statistics() -> str:
    """
    查询整个机队的统计概览，包括：按租赁状态分布、按租赁方式分布、
    按机型号分布的数量统计。

    适用场景：
    - "所有飞机的概览"
    - "机队统计信息"
    - "总共多少架飞机？各状态分布如何？"

    参数: 无
    返回:
        Markdown 格式的统计表格
    """
    return fleet_statistics()


# ═══════════════════════════════════════════════════════════
#  租金计算工具（保留不变）
# ═══════════════════════════════════════════════════════════

@tool
def rent_calculator(query: str) -> str:
    """
    根据飞机的租金单价和使用量，动态计算实际租金金额。

    适用场景：
    - "B-7378 这个月飞了 240 小时，租金是多少？"
    - "B-3201 租了 6 个月，总租金多少钱？"
    - "B-3509 如果租 3 年，总租金多少？"
    - "所有按小时计费的飞机，按 220 小时/月算一下租金"

    不适用场景：
    - 仅查单价不涉及计算（请用 get_aircraft_rental_price）

    参数:
        query: 租金计算查询，需包含注册号和用量（小时数/月数/年数）
    返回:
        格式化的计算结果
    """
    import re as _re

    df = get_aircraft_df()
    query_upper = query.upper()

    # 提取注册号
    reg_pattern = r"B-\d{4}"
    reg_matches = _re.findall(reg_pattern, query_upper)
    if not reg_matches:
        return (
            "请在查询中提供飞机注册号（如 B-7378）和用量信息。\n"
            "例如：「B-7378 飞了 240 小时，租金多少？」\n"
            "或  「B-3201 租了 6 个月，总租金多少？」"
        )

    # 提取使用量
    usage_match = _re.search(r"(\d+[\.,]?\d*)\s*(小时|个?月|年|天)", query)
    if not usage_match:
        reg = reg_matches[0]
        match = df[df["注册号"] == reg]
        if match.empty:
            return f"未找到注册号为 {reg} 的飞机。"
        row = match.iloc[0]
        return (
            f"**{reg}**（{row['机型号']}）的租金单价为 **{row['租金单价']}**，"
            f"计算方式为 **{row['租金计算方式']}**。\n"
            f"请提供具体使用量（飞行小时数或租赁月数），我将为您计算总租金。"
        )

    reg = reg_matches[0]
    raw_usage = float(usage_match.group(1).replace(",", ""))
    usage_unit = usage_match.group(2)

    if usage_unit in ("年",):
        usage = raw_usage * 12
    elif usage_unit in ("天",):
        usage = raw_usage / 30
    else:
        usage = raw_usage

    return calculate_rent(reg, usage)


# ═══════════════════════════════════════════════════════════
#  工具列表
# ═══════════════════════════════════════════════════════════

def get_all_tools():
    """返回 Agent 可用的全部工具列表（按需查询，精简回答）。"""
    return [
        # 单一字段查询（按需使用，回答精简）
        get_aircraft_status,
        get_aircraft_lease_type,
        get_aircraft_rental_price,
        get_aircraft_model,
        get_aircraft_lessee_lessor,
        # 全量 / 批量 / 统计
        get_aircraft_full_info,
        search_aircraft,
        get_fleet_statistics,
        # 知识 + 计算
        rag_knowledge_base,
        rent_calculator,
    ]
