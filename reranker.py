"""Custom reranker using text-embeddings-router API."""

import logging
from typing import List, Optional

import requests
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, QueryBundle

logger = logging.getLogger(__name__)


class TEIReranker(BaseNodePostprocessor):
    """Reranker using Text Embeddings Inference (TEI) API.

    This reranker calls a local TEI service for reranking documents.
    TEI should be running with a rerank model like:
    cross-encoder/ms-marco-MiniLM-L-6-v2

    Args:
        api_url: URL of the TEI rerank endpoint (e.g., "http://localhost:8099")
        top_n: Number of documents to return after reranking
        timeout: Request timeout in seconds
    """

    api_url: str
    top_n: int
    timeout: int

    def __init__(
        self,
        api_url: str = "http://localhost:9999",
        top_n: int = 3,
        timeout: int = 30,
    ):
        """Initialize TEI reranker."""
        super().__init__(api_url=api_url, top_n=top_n, timeout=timeout)

        # 验证 API 是否可用
        self._verify_api()

    def _verify_api(self) -> None:
        """Verify that the TEI API is accessible."""
        try:
            # 尝试访问健康检查端点
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ TEI Rerank API 连接成功: {self.api_url}")
            else:
                logger.warning(f"⚠️  TEI API 返回非 200 状态码: {response.status_code}")
        except Exception as e:
            logger.warning(
                f"⚠️  无法连接到 TEI API ({self.api_url}): {e}\n"
                "请确保 text-embeddings-router 正在运行"
            )

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        """Rerank nodes using TEI API.

        Args:
            nodes: List of nodes with scores from retrieval
            query_bundle: Query information

        Returns:
            Reranked list of nodes with updated scores
        """
        if not query_bundle:
            return nodes

        if len(nodes) == 0:
            return []

        query_str = query_bundle.query_str

        # 准备文档文本列表
        texts = [node.node.get_content() for node in nodes]

        try:
            # 调用 TEI rerank API
            response = requests.post(
                f"{self.api_url}/rerank",
                json={
                    "query": query_str,
                    "texts": texts,
                    "truncate": True,  # 自动截断过长文本
                },
                timeout=self.timeout,
            )
            response.raise_for_status()

            # 解析返回结果
            rerank_results = response.json()

            # TEI 返回格式: [{"index": 0, "score": 0.95}, ...]
            # 已经按 score 降序排列
            reranked_nodes = []
            for result in rerank_results[: self.top_n]:
                idx = result["index"]
                score = result["score"]

                # 更新节点分数
                node = nodes[idx]
                node.score = score
                reranked_nodes.append(node)

            logger.info(f"🎯 Rerank 完成: {len(nodes)} → {len(reranked_nodes)} 个文档")

            return reranked_nodes

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ TEI Rerank API 调用失败: {e}")
            logger.warning("⚠️  回退到原始检索结果")
            # 如果 API 调用失败，返回前 top_n 个原始结果
            return nodes[: self.top_n]
        except Exception as e:
            logger.error(f"❌ Rerank 处理错误: {e}")
            return nodes[: self.top_n]
