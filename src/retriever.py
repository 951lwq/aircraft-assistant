"""
RAG 检索 + 问答链。
加载 Chroma 向量库，创建 LangChain RetrievalQA 链。
"""

from langchain_openai import ChatOpenAI
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma

from src.config import config
from src.ingest import get_embeddings


# ─── 自定义 Prompt 模板 ───────────────────────────────────

RAG_PROMPT_TEMPLATE = """你是一个飞机资产管理领域的专业知识助手。
请严格根据以下已知信息回答问题。如果已知信息不足以回答问题，请如实说"根据现有资料，我无法回答这个问题"。

已知信息：
{context}

问题：{question}

回答："""

RAG_PROMPT = PromptTemplate(
    template=RAG_PROMPT_TEMPLATE,
    input_variables=["context", "question"],
)


# ─── 构建问答链 ───────────────────────────────────────────

def build_qa_chain() -> RetrievalQA:
    """
    创建并返回 RetrievalQA 链。

    步骤：
    1. 加载 Chroma 向量库作为 retriever
    2. 创建 DeepSeek Chat LLM
    3. 组装 RetrievalQA 链
    """
    config.validate()

    # 1. 向量库 → Retriever
    embeddings = get_embeddings()
    vectorstore = Chroma(
        collection_name=config.CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=config.CHROMA_PERSIST_DIR,
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": config.RETRIEVER_K}
    )

    # 2. LLM（DeepSeek API，兼容 OpenAI SDK）
    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        openai_api_key=config.DEEPSEEK_API_KEY,
        openai_api_base=config.DEEPSEEK_BASE_URL,
        temperature=0.3,  # 低温度确保回答严谨
        max_tokens=1024,
    )

    # 3. RetrievalQA 链
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # 将检索到的文档直接拼入 prompt
        retriever=retriever,
        return_source_documents=True,  # 返回引用的来源文档
        chain_type_kwargs={"prompt": RAG_PROMPT},
    )

    return qa_chain
