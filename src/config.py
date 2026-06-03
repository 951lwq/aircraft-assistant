"""
集中管理所有配置项。
通过 .env 文件和环境变量加载配置。
"""

import os
from dotenv import load_dotenv

# 加载项目根目录下的 .env 文件
load_dotenv()


class Config:
    """应用配置类，所有属性从环境变量读取，提供合理默认值。"""

    # ── DeepSeek API ──
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    # ── 模型 ──
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek-chat")
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5"
    )

    # ── 文档路径 ──
    DOC_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "doc")

    # ── 分块参数 ──
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))

    # ── Chroma ──
    CHROMA_PERSIST_DIR: str = os.getenv(
        "CHROMA_PERSIST_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db"),
    )
    CHROMA_COLLECTION_NAME: str = "aircraft_asset_management"

    # ── 检索 ──
    RETRIEVER_K: int = int(os.getenv("RETRIEVER_K", "4"))

    @classmethod
    def validate(cls) -> bool:
        """检查必要配置是否已填写。"""
        if not cls.DEEPSEEK_API_KEY or "your-api-key" in cls.DEEPSEEK_API_KEY:
            raise ValueError(
                "请先在 .env 文件中设置 DEEPSEEK_API_KEY（复制 .env.example 并修改）"
            )
        return True


# 全局单例
config = Config()
