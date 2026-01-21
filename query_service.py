"""Query service for RAG system."""

import logging

import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.embeddings.zhipuai import ZhipuAIEmbedding
from llama_index.llms.zhipuai import ZhipuAI
from llama_index.vector_stores.chroma import ChromaVectorStore

import config
from reranker import TEIReranker

logger = logging.getLogger(__name__)


class QueryService:
    """Handles querying the RAG system."""

    def __init__(self):
        """Initialize query service."""
        # 验证 API key
        if not config.ZHIPUAI_API_KEY:
            raise ValueError("❌ ZHIPUAI_API_KEY 未设置！请在 .env 文件中配置 API key")

        # 配置模型
        self.llm = ZhipuAI(
            model=config.LLM_MODEL,
            api_key=config.ZHIPUAI_API_KEY,
        )

        self.embed_model = ZhipuAIEmbedding(
            model=config.EMBEDDING_MODEL,
            api_key=config.ZHIPUAI_API_KEY,
        )

        Settings.llm = self.llm
        Settings.embed_model = self.embed_model

        # 连接到现有的 Chroma 数据库
        self.chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)

        try:
            self.chroma_collection = self.chroma_client.get_collection(
                name=config.COLLECTION_NAME
            )
        except Exception as e:
            raise RuntimeError(
                f"❌ 未找到索引！请先运行 'python indexer.py' 构建索引。\n错误: {e}"
            )

        # 从现有存储加载索引
        vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=self.embed_model,
        )

        # 配置 node postprocessors（包括 rerank）
        node_postprocessors = self._setup_postprocessors()

        # 创建查询引擎
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=config.SIMILARITY_TOP_K,
            response_mode="compact",
            node_postprocessors=node_postprocessors,
        )

        logger.info("✅ 查询服务初始化完成")

    def _setup_postprocessors(self) -> list:
        """Setup node postprocessors including reranker.

        Returns:
            List of postprocessors to apply to retrieved nodes.
        """
        postprocessors = []

        if config.USE_RERANK:
            try:
                reranker = TEIReranker(
                    api_url=config.RERANK_API_URL,
                    top_n=config.RERANK_TOP_N,
                    timeout=config.RERANK_TIMEOUT,
                )
                postprocessors.append(reranker)
                logger.info(
                    f"✅ TEI Rerank 启用: {config.RERANK_API_URL}, "
                    f"初始检索={config.SIMILARITY_TOP_K}, "
                    f"rerank后={config.RERANK_TOP_N}"
                )
            except Exception as e:
                logger.warning(f"⚠️  Rerank 初始化失败: {e}")

        return postprocessors

    def query(self, question: str, return_sources: bool = True):
        """Query the RAG system.

        Args:
            question: The question to query.
            return_sources: Whether to return source nodes.

        Returns:
            Dictionary containing question, answer, and optional sources.
        """
        logger.info(f"🔍 查询: {question}")

        response = self.query_engine.query(question)

        result = {
            "question": question,
            "answer": str(response),
            "sources": [],
        }

        if return_sources and hasattr(response, "source_nodes"):
            for i, node in enumerate(response.source_nodes, 1):
                source = {
                    "chunk_id": i,
                    "score": node.score,
                    "text": node.text[:100] + "..."
                    if len(node.text) > 100
                    else node.text,
                    "metadata": node.node.metadata,
                }
                result["sources"].append(source)

        return result


def main():
    """Interactive query mode."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    service = QueryService()

    print("\n" + "=" * 70)
    print("💬 RAG 查询服务 (输入 'quit' 退出)")
    print("=" * 70)

    while True:
        question = input("\n❓ 请输入问题: ").strip()
        if question.lower() in ["quit", "exit", "q"]:
            break

        if not question:
            continue

        result = service.query(question)

        print("\n" + "=" * 70)
        print("💡 回答:")
        print("-" * 70)
        print(result["answer"])

        if result["sources"]:
            print("\n" + "=" * 70)
            print("📚 相关来源:")
            for src in result["sources"]:
                print(f"\n📄 来源 {src['chunk_id']} (相似度: {src['score']:.4f})")
                print(f"   {src['text']}")
                print(f"   📌 {src['metadata']}")
        print("=" * 70)


if __name__ == "__main__":
    main()
