"""
飞机模拟数据库：10 架飞机的租赁状态与财务信息。
使用 Pandas DataFrame 存储，支持灵活查询。
"""

import pandas as pd
from typing import Optional, List, Dict, Any


# ─── 模拟数据定义 ──────────────────────────────────────────

DATA = [
    {
        "注册号": "B-3201",
        "机型号": "Airbus A320",
        "租赁状态": "在租",
        "承租方": "中国东方航空",
        "出租方": "工银金融租赁",
        "租赁方式": "经营租赁",
        "租金计算方式": "固定月租金",
        "租金单价": "3,500 USD/月",
        "市场费率参考": "3,200-3,800 USD/月",
        "当前租金金额": "3,500 USD",
    },
    {
        "注册号": "B-7378",
        "机型号": "Boeing 737-800",
        "租赁状态": "在租",
        "承租方": "中国南方航空",
        "出租方": "国银金融租赁",
        "租赁方式": "融资租赁",
        "租金计算方式": "按飞行小时",
        "租金单价": "200 USD/小时",
        "市场费率参考": "180-220 USD/小时",
        "当前租金金额": "48,000 USD",
    },
    {
        "注册号": "B-3202",
        "机型号": "Airbus A320",
        "租赁状态": "维修中",
        "承租方": "中国东方航空",
        "出租方": "工银金融租赁",
        "租赁方式": "经营租赁",
        "租金计算方式": "固定月租金",
        "租金单价": "3,500 USD/月",
        "市场费率参考": "3,200-3,800 USD/月",
        "当前租金金额": "3,500 USD",
    },
    {
        "注册号": "B-7879",
        "机型号": "Boeing 787-9",
        "租赁状态": "在租",
        "承租方": "中国国际航空",
        "出租方": "中银航空租赁",
        "租赁方式": "经营租赁",
        "租金计算方式": "固定月租金",
        "租金单价": "8,500 USD/月",
        "市场费率参考": "8,000-9,000 USD/月",
        "当前租金金额": "8,500 USD",
    },
    {
        "注册号": "B-7375",
        "机型号": "Boeing 737-800",
        "租赁状态": "退租中",
        "承租方": "海南航空",
        "出租方": "交银金融租赁",
        "租赁方式": "经营租赁",
        "租金计算方式": "固定月租金",
        "租金单价": "3,400 USD/月",
        "市场费率参考": "3,100-3,600 USD/月",
        "当前租金金额": "0 USD (退租清算中)",
    },
    {
        "注册号": "B-3205",
        "机型号": "Airbus A320neo",
        "租赁状态": "在租",
        "承租方": "春秋航空",
        "出租方": "建信金融租赁",
        "租赁方式": "经营租赁",
        "租金计算方式": "按飞行小时",
        "租金单价": "230 USD/小时",
        "市场费率参考": "210-250 USD/小时",
        "当前租金金额": "52,900 USD",
    },
    {
        "注册号": "B-3302",
        "机型号": "Airbus A330-300",
        "租赁状态": "在租",
        "承租方": "中国南方航空",
        "出租方": "工银金融租赁",
        "租赁方式": "融资租赁",
        "租金计算方式": "固定月租金",
        "租金单价": "7,200 USD/月",
        "市场费率参考": "6,800-7,500 USD/月",
        "当前租金金额": "7,200 USD",
    },
    {
        "注册号": "B-7376",
        "机型号": "Boeing 737-800",
        "租赁状态": "维修中",
        "承租方": "厦门航空",
        "出租方": "国银金融租赁",
        "租赁方式": "融资租赁",
        "租金计算方式": "按飞行小时",
        "租金单价": "195 USD/小时",
        "市场费率参考": "180-220 USD/小时",
        "当前租金金额": "35,100 USD",
    },
    {
        "注册号": "B-3509",
        "机型号": "Airbus A350-900",
        "租赁状态": "在租",
        "承租方": "中国国际航空",
        "出租方": "中银航空租赁",
        "租赁方式": "经营租赁",
        "租金计算方式": "固定月租金",
        "租金单价": "11,000 USD/月",
        "市场费率参考": "10,500-12,000 USD/月",
        "当前租金金额": "11,000 USD",
    },
    {
        "注册号": "B-3218",
        "机型号": "Airbus A320",
        "租赁状态": "待交付",
        "承租方": "吉祥航空",
        "出租方": "招银金融租赁",
        "租赁方式": "经营租赁",
        "租金计算方式": "固定月租金",
        "租金单价": "3,600 USD/月",
        "市场费率参考": "3,300-3,900 USD/月",
        "当前租金金额": "0 USD (尚未交付)",
    },
]


# ─── DataFrame 构建 ────────────────────────────────────────

def load_aircraft_df() -> pd.DataFrame:
    """返回飞机模拟数据 DataFrame。"""
    return pd.DataFrame(DATA)


def get_schema_description() -> str:
    """返回数据表结构的文字描述，供 Agent 理解数据字段含义。"""
    return """
飞机数据库字段说明（共 10 条记录）：
- 注册号：飞机的唯一注册编号，如 B-3201
- 机型号：飞机型号，如 Airbus A320, Boeing 737-800, Airbus A320neo, Boeing 787-9, Airbus A330-300, Airbus A350-900
- 租赁状态：在租 / 维修中 / 退租中 / 待交付
- 承租方：租赁飞机的航空公司，如 中国东方航空、中国南方航空、中国国际航空、海南航空、春秋航空、厦门航空、吉祥航空
- 出租方：提供飞机租赁的金融机构，如 工银金融租赁、国银金融租赁、中银航空租赁、交银金融租赁、建信金融租赁、招银金融租赁
- 租赁方式：经营租赁 / 融资租赁
- 租金计算方式：固定月租金 / 按飞行小时
- 租金单价：每单位时间的租金价格
- 市场费率参考：当前市场上同类机型的费率范围
- 当前租金金额：当前实际收取的租金金额
"""


# ─── 纯文本列表格式化（无 Markdown 标记） ────────────────

def _df_to_plain(df: pd.DataFrame) -> str:
    """
    将 DataFrame 转为纯文本格式，每行格式：
      注册号 | 机型号 | 租赁状态 | ...
      B-3201 | Airbus A320 | 在租 | ...
    不使用任何 Markdown 标记（无 **、无 |--|、无 | 包围）。
    """
    if df.empty:
        return "（无数据）"

    headers = list(df.columns)
    rows = df.values.tolist()

    # 计算每列宽度
    def _display_width(s: str) -> int:
        w = 0
        for ch in str(s):
            w += 2 if "一" <= ch <= "鿿" else 1
        return w

    col_widths = [_display_width(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], _display_width(str(cell)))

    def _pad(s: str, width: int) -> str:
        text = str(s)
        dw = _display_width(text)
        return text + " " * (width - dw)

    lines = []
    # 表头
    lines.append("  " + " | ".join(_pad(h, col_widths[i]) for i, h in enumerate(headers)))
    # 分隔
    lines.append("  " + "-+-".join("-" * col_widths[i] for i in range(len(headers))))
    # 数据行
    for row in rows:
        lines.append("  " + " | ".join(_pad(str(cell), col_widths[i]) for i, cell in enumerate(row)))

    return "\n".join(lines)


def query_dataframe(df: pd.DataFrame, query_text: str) -> str:
    """
    根据自然语言查询文本，在 DataFrame 上执行关键词检索，
    返回格式化的查询结果字符串。

    支持的关键词匹配维度：注册号、机型号、租赁状态、承租方、
    出租方、租赁方式、租金计算方式。
    """
    result_df = df.copy()

    # ── 关键词匹配逻辑 ──
    query_lower = query_text.lower()

    # 机型匹配
    model_keywords = {
        "a320": "A320",
        "a320neo": "A320neo",
        "a330": "A330",
        "a350": "A350",
        "737": "737",
        "737-800": "737-800",
        "787": "787",
        "787-9": "787-9",
    }
    matched_models = []
    for kw, model in model_keywords.items():
        if kw in query_lower:
            matched_models.append(model)
    if matched_models:
        # 部分匹配（如 "A320" 匹配 "Airbus A320" 和 "Airbus A320neo"）
        result_df = result_df[
            result_df["机型号"].apply(
                lambda x: any(m in x for m in matched_models)
            )
        ]

    # 租赁状态匹配
    status_keywords = {
        "在租": "在租",
        "维修": "维修中",
        "退租": "退租中",
        "交付": "待交付",
        "待交付": "待交付",
    }
    for kw, status in status_keywords.items():
        if kw in query_text:
            result_df = result_df[result_df["租赁状态"] == status]
            break

    # 承租方匹配
    airline_keywords = [
        "东方航空", "南方航空", "国际航空", "海南航空",
        "春秋航空", "厦门航空", "吉祥航空",
    ]
    for airline in airline_keywords:
        if airline in query_text:
            result_df = result_df[result_df["承租方"].str.contains(airline)]
            break

    # 出租方匹配
    lessor_keywords = [
        "工银", "国银", "中银", "交银", "建信", "招银",
    ]
    for lessor in lessor_keywords:
        if lessor in query_text:
            result_df = result_df[result_df["出租方"].str.contains(lessor)]
            break

    # 租赁方式匹配
    if "融资租赁" in query_text:
        result_df = result_df[result_df["租赁方式"] == "融资租赁"]
    elif "经营租赁" in query_text:
        result_df = result_df[result_df["租赁方式"] == "经营租赁"]

    # 租金计算方式匹配
    if "按飞行小时" in query_text or "飞行小时" in query_text:
        result_df = result_df[result_df["租金计算方式"] == "按飞行小时"]
    elif "固定月租金" in query_text or "固定" in query_text:
        result_df = result_df[result_df["租金计算方式"] == "固定月租金"]

    # 注册号精确匹配
    for _, row in df.iterrows():
        reg = row["注册号"]
        if reg.lower() in query_lower:
            result_df = df[df["注册号"] == reg]
            break

    # ── 格式化返回（纯文本）──
    if result_df.empty:
        return "未找到匹配的飞机记录，请调整查询条件。"

    table_plain = _df_to_plain(result_df)
    return f"查询到 {len(result_df)} 条记录：\n\n{table_plain}"


def get_full_dataset_summary(df: pd.DataFrame) -> str:
    """返回全量数据的摘要统计（纯文本格式）。"""
    lines = [f"数据库共 {len(df)} 架飞机。\n"]

    lines.append("按租赁状态分布：")
    status_df = df["租赁状态"].value_counts().reset_index()
    status_df.columns = ["租赁状态", "数量"]
    lines.append(_df_to_plain(status_df))
    lines.append("")

    lines.append("按租赁方式分布：")
    type_df = df["租赁方式"].value_counts().reset_index()
    type_df.columns = ["租赁方式", "数量"]
    lines.append(_df_to_plain(type_df))
    lines.append("")

    lines.append("按机型号分布：")
    model_df = df["机型号"].value_counts().reset_index()
    model_df.columns = ["机型号", "数量"]
    lines.append(_df_to_plain(model_df))

    return "\n".join(lines)


# ─── 租金动态计算 ──────────────────────────────────────────

import re


def parse_rate(rate_str: str) -> tuple:
    """
    解析租金单价字符串，返回 (数值, 单位)。

    示例:
        "3,500 USD/月"   → (3500.0, "月")
        "200 USD/小时"   → (200.0, "小时")
        "0 USD (退租清算中)" → (0.0, "月")
        "0 USD (尚未交付)"   → (0.0, "月")
    """
    # 提取数值部分（去掉逗号）
    match = re.search(r"([\d,]+)\s*USD", rate_str)
    if not match:
        return (0.0, "月")

    value = float(match.group(1).replace(",", ""))

    # 提取单位
    if "小时" in rate_str:
        unit = "小时"
    else:
        unit = "月"

    return (value, unit)


def calculate_rent(reg_number: str, usage: float) -> str:
    """
    根据飞机注册号和使用量，计算实时租金。

    参数:
        reg_number: 飞机注册号，如 "B-7378"
        usage: 使用量（月数或小时数，由飞机的租金计算方式决定）

    返回:
        纯文本格式的计算结果
    """
    df = get_aircraft_df()
    match = df[df["注册号"] == reg_number.upper()]
    if match.empty:
        return f"未找到注册号为 {reg_number} 的飞机。可用注册号：{', '.join(df['注册号'].tolist())}"

    row = match.iloc[0]
    calc_method = row["租金计算方式"]
    rate_str = row["租金单价"]
    unit_rate, unit = parse_rate(rate_str)

    if unit_rate == 0:
        return (
            f"{reg_number}（{row['机型号']}）当前处于 {row['租赁状态']} 状态，"
            f"无法计算租金。（原因：{row['当前租金金额']}）"
        )

    total = unit_rate * usage

    lines = [
        f"{reg_number} 租金计算：",
        f"  注册号: {reg_number}",
        f"  机型号: {row['机型号']}",
        f"  承租方: {row['承租方']}",
        f"  租赁方式: {row['租赁方式']}",
        f"  租金计算方式: {calc_method}",
        f"  单价: {rate_str}",
        f"  市场费率参考: {row['市场费率参考']}",
        f"  使用量: {usage:,.0f} {unit}",
        f"  计算结果: {total:,.0f} USD",
        f"",
        f"计算过程：{unit_rate:,.0f} USD/{unit} x {usage:,.0f} {unit} = {total:,.0f} USD",
    ]
    return "\n".join(lines)


def calculate_all_hourly_rates(hours: float = 220) -> str:
    """
    批量计算所有"按飞行小时"计费的飞机的月度租金。

    参数:
        hours: 当月飞行小时数（默认 220 小时，约等于常规月利用率）

    返回:
        纯文本格式的计算结果表
    """
    df = get_aircraft_df()
    hourly_df = df[df["租金计算方式"] == "按飞行小时"].copy()

    if hourly_df.empty:
        return "当前没有按飞行小时计费的飞机。"

    rows_list = []
    grand_total = 0
    for _, row in hourly_df.iterrows():
        rate, _ = parse_rate(row["租金单价"])
        total = rate * hours
        grand_total += total
        rows_list.append([
            row["注册号"],
            row["机型号"],
            row["承租方"],
            row["租金单价"],
            f"{hours:,} 小时",
            f"{total:,.0f} USD",
        ])

    result_df = pd.DataFrame(
        rows_list,
        columns=["注册号", "机型号", "承租方", "单价", "当月飞行量", "当月租金"],
    )

    return (
        f"按飞行小时计费飞机，月度租金估算（假设当月 {hours:,} 小时）：\n\n"
        + _df_to_plain(result_df)
        + f"\n\n合计：{grand_total:,.0f} USD"
    )


# ─── 精准查询函数（供 tools.py 各工具调用） ───────────────

def _find(reg_no: str) -> tuple:
    """
    根据注册号查找飞机。成功返回 (row, None)，失败返回 (None, error_msg)。
    reg_no 大小写不敏感。
    """
    df = get_aircraft_df()
    reg = reg_no.upper().strip()
    match = df[df["注册号"] == reg]
    if match.empty:
        return (None, f"未找到注册号为 {reg} 的飞机。可用注册号：{', '.join(df['注册号'].tolist())}")
    return (match.iloc[0], None)


def lookup_status(reg_no: str) -> str:
    """返回仅含状态的精简回答（纯文本，无 Markdown）。"""
    row, err = _find(reg_no)
    if err:
        return err
    return f"{row['注册号']}（{row['机型号']}）当前状态：{row['租赁状态']}"


def lookup_lease_type(reg_no: str) -> str:
    """返回仅含租赁方式的精简回答（纯文本）。"""
    row, err = _find(reg_no)
    if err:
        return err
    return f"{row['注册号']}（{row['机型号']}）租赁方式：{row['租赁方式']}"


def lookup_rental_price(reg_no: str) -> str:
    """返回租金单价 + 计算方式 + 市场费率的精简回答（纯文本）。"""
    row, err = _find(reg_no)
    if err:
        return err
    return (
        f"{row['注册号']}（{row['机型号']}）租金信息：\n"
        f"  租金计算方式: {row['租金计算方式']}\n"
        f"  租金单价: {row['租金单价']}\n"
        f"  市场费率参考: {row['市场费率参考']}"
    )


def lookup_model(reg_no: str) -> str:
    """返回仅含机型信息的精简回答（纯文本）。"""
    row, err = _find(reg_no)
    if err:
        return err
    return f"{row['注册号']} 机型：{row['机型号']}"


def lookup_lessee_lessor(reg_no: str) -> str:
    """返回承租方 + 出租方信息（纯文本）。"""
    row, err = _find(reg_no)
    if err:
        return err
    return (
        f"{row['注册号']}（{row['机型号']}）\n"
        f"  承租方: {row['承租方']}\n"
        f"  出租方: {row['出租方']}"
    )


def lookup_full_info(reg_no: str) -> str:
    """返回全量信息（纯文本，仅用户明确要"详细信息"时使用）。"""
    row, err = _find(reg_no)
    if err:
        return err
    lines = [f"{row['注册号']} 完整信息：", ""]
    for col in ["注册号", "机型号", "租赁状态", "承租方", "出租方",
                 "租赁方式", "租金计算方式", "租金单价", "市场费率参考", "当前租金金额"]:
        lines.append(f"  {col}: {row[col]}")
    return "\n".join(lines)


def search_fleet(query: str) -> str:
    """
    按条件搜索飞机（机型/状态/航空公司/租赁方式等），返回匹配的 Markdown 表格。
    保留原有的多维关键词过滤逻辑，但只用于批量搜索场景。
    """
    return query_dataframe(get_aircraft_df(), query)


def fleet_statistics() -> str:
    """返回全量统计摘要。"""
    return get_full_dataset_summary(get_aircraft_df())


# ─── 模块加载即初始化 ─────────────────────────────────────

_aircraft_df: Optional[pd.DataFrame] = None


def get_aircraft_df() -> pd.DataFrame:
    """单例模式获取 DataFrame。"""
    global _aircraft_df
    if _aircraft_df is None:
        _aircraft_df = load_aircraft_df()
    return _aircraft_df
