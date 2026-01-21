"""Test script for TEI reranker."""

import logging

from llama_index.core.schema import NodeWithScore, QueryBundle, TextNode

from reranker import TEIReranker

logging.basicConfig(level=logging.INFO)


def test_reranker():
    """Test TEI reranker connection and functionality."""
    print("=" * 70)
    print("🧪 测试 TEI Reranker")
    print("=" * 70)

    # 创建 reranker 实例
    reranker = TEIReranker(
        api_url="http://localhost:8099",
        top_n=2,
    )

    # 模拟查询和文档
    query = "什么是 RAG？"

    # 创建测试节点
    nodes = [
        NodeWithScore(
            node=TextNode(
                text="RAG 是检索增强生成（Retrieval-Augmented Generation）的缩写"
            ),
            score=0.8,
        ),
        NodeWithScore(
            node=TextNode(text="今天天气很好，阳光明媚"),
            score=0.75,
        ),
        NodeWithScore(
            node=TextNode(text="RAG 系统结合了检索和生成两个步骤"),
            score=0.78,
        ),
    ]

    query_bundle = QueryBundle(query_str=query)

    # 执行 rerank
    reranked = reranker._postprocess_nodes(nodes, query_bundle)

    print(f"\n查询: {query}")
    print(f"\n原始顺序 ({len(nodes)} 个文档):")
    for i, node in enumerate(nodes, 1):
        print(f"{i}. [分数: {node.score:.4f}] {node.node.text[:50]}...")

    print(f"\nRerank 后 (Top {len(reranked)}):")
    for i, node in enumerate(reranked, 1):
        print(f"{i}. [分数: {node.score:.4f}] {node.node.text[:50]}...")

    print("\n" + "=" * 70)
    print("✅ 测试完成")


if __name__ == "__main__":
    test_reranker()
