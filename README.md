# 飞机资产管理知识助手（RAG + Agent）

基于 RAG + LangChain Agent 的飞机资产管理领域智能问答系统，支持知识库检索与飞机数据库查询的自动路由。

## 技术栈

- **大模型**: DeepSeek API (`deepseek-chat`)
- **Embedding**: HuggingFace `BAAI/bge-small-zh-v1.5`（本地中文模型）
- **向量库**: Chroma（本地持久化）
- **框架**: LangChain（RAG + Agent）
- **PDF 解析**: PyMuPDF

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 DeepSeek API Key 和 Base URL
```

### 3. 摄入文档

```bash
python -m src.ingest          # 首次运行，或文档有变化时
python -m src.ingest --force  # 强制重建
```

### 4. 启动问答

**纯 RAG 模式**（仅知识库问答）：

```bash
python -m src.cli
```

**Agent 模式**（知识库 + 飞机数据库，自动路由）：

```bash
python -m src.cli_agent        # 标准模式
python -m src.cli_agent -v     # 详细模式（显示 Agent 推理过程）
```

输入 `quit` 退出。

## 两种模式对比

| 模式 | 命令 | 能力 |
|------|------|------|
| 纯 RAG | `python -m src.cli` | 查文档知识（租赁方式、管理流程、LLP、退租等） |
| Agent | `python -m src.cli_agent` | 查文档知识 **+** 飞机数据库（状态、租金、承租方等），自动路由 |

## Agent 自动路由示例

```
You: 什么是经营租赁？
→ 自动调用 rag_knowledge_base → 知识库回答

You: A320的飞机有哪些？
→ 自动调用 aircraft_database → 4 架 A320 详细信息

You: B-3201的租金和状态？
→ 自动调用 aircraft_database → 单架飞机详情

You: 在租状态的飞机有几架？
→ 自动调用 aircraft_database → 统计结果

You: 工银金融租赁的飞机有哪些？融资租赁和经营租赁有什么区别？
→ 自动调用 aircraft_database + rag_knowledge_base → 综合回答
```

## 飞机模拟数据库

10 架飞机，字段包括：

| 字段 | 说明 |
|------|------|
| 注册号 | 唯一编号（B-3201, B-7378, ...） |
| 机型号 | A320, 737-800, 787-9, A330-300, A350-900, A320neo |
| 租赁状态 | 在租 / 维修中 / 退租中 / 待交付 |
| 承租方 | 东航、南航、国航、海航、春秋、厦航、吉祥 |
| 出租方 | 工银、国银、中银、交银、建信、招银 |
| 租赁方式 | 经营租赁 / 融资租赁 |
| 租金计算 | 固定月租金 / 按飞行小时 |

## 项目结构

```
├── doc/                      # 原始文档
│   ├── 租赁方式.txt
│   ├── 飞机资产管理流程.txt
│   └── 飞机资产管理.pdf
├── src/
│   ├── config.py             # 配置管理（.env 加载）
│   ├── ingest.py             # 文档摄入（TXT/PDF → 分块 → Chroma）
│   ├── retriever.py          # RAG RetrievalQA 链
│   ├── cli.py                # 纯 RAG 命令行
│   ├── tools.py              # Agent 工具定义（RAG + DB）
│   ├── agent.py              # LangChain Agent（自动路由）
│   ├── cli_agent.py          # Agent 命令行
│   └── data/
│       └── aircraft_data.py  # 飞机模拟数据库（10 架）
├── chroma_db/                # Chroma 向量库（自动生成）
├── .env / .env.example
├── requirements.txt
└── README.md
```

## 配置说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | **必填** |
| `DEEPSEEK_BASE_URL` | API 地址 | `https://api.deepseek.com` |
| `LLM_MODEL` | 对话模型 | `deepseek-chat` |
| `EMBEDDING_MODEL` | 向量化模型 | `BAAI/bge-small-zh-v1.5` |
| `CHUNK_SIZE` | 分块大小 | `500` |
| `CHUNK_OVERLAP` | 分块重叠 | `50` |
| `RETRIEVER_K` | 检索返回数 | `4` |
