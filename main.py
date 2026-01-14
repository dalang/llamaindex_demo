"""Starter script for LlamaIndex RAG using Zhipu AI glm-4-plus model."""

import logging
import os
import sys

from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.embeddings.zhipuai import ZhipuAIEmbedding
from llama_index.llms.zhipuai import ZhipuAI

# 可选：启用 DEBUG 日志
# logging.basicConfig(stream=sys.stdout, level=logging.INFO)

load_dotenv()

llm = ZhipuAI(
    model="glm-4-plus",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
)

embed_model = ZhipuAIEmbedding(
    model="embedding-2",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
)

Settings.llm = llm
Settings.embed_model = embed_model

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
print(f"Index created successfully.{index}")


def print_embedding_info(text: str, embedding: list):
    """打印 embedding 的详细信息"""
    print(f"\n{'=' * 70}")
    print(f"📝 文本: '{text}'")
    print(f"{'=' * 70}")
    print(f"🎯 向量维度: {len(embedding)}")
    print(f"📊 数据类型: {type(embedding[0])}")
    print(f"📈 取值范围: [{min(embedding):.6f}, {max(embedding):.6f}]")

    print(f"\n🔢 向量前 30 维:")
    for i in range(min(30, len(embedding))):
        print(f"  [{i:3d}] {embedding[i]:9.6f}", end="")
        if (i + 1) % 5 == 0:
            print()  # 每 5 个换行


# 配置查询引擎，增加检索数量
query_engine = index.as_query_engine(
    similarity_top_k=3,  # 检索 3 个最相关的片段
    response_mode="compact",
)

if __name__ == "__main__":
    query_str = "What did the author do in college?"
    response = query_engine.query(query_str)

    embedding = embed_model.get_query_embedding(query_str)
    print_embedding_info(query_str, embedding)

    # 打印检索到的相关片段
    print("\n" + "=" * 70)
    print("🔍 检索到的相关文档片段：")
    print("=" * 70)
    for i, node in enumerate(response.source_nodes, 1):
        print(f"\n📄 片段 {i} (相似度分数: {node.score:.4f})")
        print("-" * 70)
        print(node.text[:500])  # 只显示前 500 字符
        if len(node.text) > 500:
            print("... (内容过长，已截断)")
        print(f"\n📌 元数据: {node.node.metadata}")

    print("\n" + "=" * 70)
    print("💡 最终回答：")
    print("=" * 70)
    print(response)
    print("=" * 70)
