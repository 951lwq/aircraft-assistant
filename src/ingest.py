"""
文档摄入脚本。
读取 doc/ 目录下的 .txt 和 .pdf 文件，分块后存入 Chroma 向量库。
支持幂等：已摄入的文档不会重复处理。
"""

import os
import hashlib
from typing import List

import os as _os
_os.environ.setdefault("CHROMA_ANONYMIZED_TELEMETRY", "False")
_os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

import fitz  # PyMuPDF
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from src.config import config


# ─── 文档加载器 ────────────────────────────────────────────

def load_txt(file_path: str) -> List[Document]:
    """加载 .txt 文件，返回 LangChain Document 列表。"""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    return [Document(page_content=text, metadata={"source": os.path.basename(file_path)})]


def load_pdf(file_path: str) -> List[Document]:
    """使用 PyMuPDF 加载 .pdf 文件，每页为一个 Document。"""
    docs = []
    doc = fitz.open(file_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():  # 跳过空白页
            docs.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": os.path.basename(file_path),
                        "page": page_num + 1,
                    },
                )
            )

    doc.close()
    return docs


def load_documents(doc_dir: str) -> List[Document]:
    """遍历 doc_dir，加载所有 .txt 和 .pdf 文件。"""
    all_docs: List[Document] = []

    if not os.path.exists(doc_dir):
        print(f"[警告] 文档目录不存在: {doc_dir}")
        return all_docs

    for filename in sorted(os.listdir(doc_dir)):
        file_path = os.path.join(doc_dir, filename)

        if filename.endswith(".txt"):
            print(f"[加载 TXT] {filename}")
            all_docs.extend(load_txt(file_path))

        elif filename.endswith(".pdf"):
            print(f"[加载 PDF] {filename}")
            all_docs.extend(load_pdf(file_path))

        else:
            print(f"[跳过] {filename} (不支持的文件类型)")

    print(f"\n共加载 {len(all_docs)} 个原始文档片段")
    return all_docs


# ─── 分块 ──────────────────────────────────────────────────

def split_documents(docs: List[Document]) -> List[Document]:
    """使用 RecursiveCharacterTextSplitter 将文档切分为 chunk。"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "；", "，", " ", ""],
        length_function=len,
    )

    chunks = splitter.split_documents(docs)
    print(f"分块完成：{len(docs)} 个原始文档 → {len(chunks)} 个 chunk")
    return chunks


# ─── Embedding & 向量存储 ──────────────────────────────────

def get_embeddings():
    """创建本地中文 Embedding 模型（HuggingFace sentence-transformers）。"""
    return HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def compute_docs_hash(chunks: List[Document]) -> str:
    """计算文档块集合的哈希，用于幂等判断。"""
    hasher = hashlib.md5()
    for chunk in chunks:
        hasher.update(chunk.page_content.encode("utf-8"))
        hasher.update(chunk.metadata.get("source", "").encode("utf-8"))
    return hasher.hexdigest()


def ingest(force: bool = False) -> Chroma:
    """
    执行完整的文档摄入流程：
    1. 加载 doc/ 下的所有 txt 和 pdf
    2. 分块
    3. 生成 embedding 并存入 Chroma

    参数:
        force: 为 True 时强制重建，否则跳过已摄入的相同内容。
    返回:
        Chroma 向量库实例。
    """
    config.validate()

    # 1. 加载
    docs = load_documents(config.DOC_DIR)
    if not docs:
        raise RuntimeError(f"未找到任何可处理的文档，请检查 {config.DOC_DIR}")

    # 2. 分块
    chunks = split_documents(docs)

    # 3. 幂等检查
    embeddings = get_embeddings()
    current_hash = compute_docs_hash(chunks)

    if not force and os.path.exists(config.CHROMA_PERSIST_DIR):
        try:
            existing_store = Chroma(
                collection_name=config.CHROMA_COLLECTION_NAME,
                embedding_function=embeddings,
                persist_directory=config.CHROMA_PERSIST_DIR,
            )
            stored_hash = existing_store._collection.metadata.get("docs_hash")
            if stored_hash == current_hash:
                print("\n[跳过] 向量库已存在且内容一致，无需重新摄入。")
                print("  使用 force=True 强制重建。")
                return existing_store
        except Exception:
            pass  # 无法读取则重建

    # 4. 存入 Chroma
    print(f"\n[存储] 正在生成 Embedding 并存入 Chroma...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=config.CHROMA_COLLECTION_NAME,
        persist_directory=config.CHROMA_PERSIST_DIR,
    )
    # 保存文档哈希到集合元数据，用于幂等判断
    vectorstore._collection.modify(metadata={"docs_hash": current_hash})

    print(f"[完成] 已存入 {len(chunks)} 个 chunk 到 Chroma")
    print(f"  持久化路径: {config.CHROMA_PERSIST_DIR}")
    return vectorstore


# ─── CLI 入口 ──────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    force_flag = "--force" in sys.argv
    ingest(force=force_flag)
