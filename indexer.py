"""Document indexing script with vector database persistence."""

import os
from pathlib import Path

import chromadb
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.embeddings.zhipuai import ZhipuAIEmbedding
from llama_index.llms.zhipuai import ZhipuAI
from llama_index.vector_stores.chroma import ChromaVectorStore

import config


class DocumentIndexer:
    """Handles document indexing and storage."""

    def __init__(self):
        """Initialize indexer with models and vector store."""
        # 配置 LLM
        self.llm = ZhipuAI(
            model=config.LLM_MODEL,
            api_key=config.ZHIPUAI_API_KEY,
        )

        # 配置嵌入模型
        self.embed_model = ZhipuAIEmbedding(
            model=config.EMBEDDING_MODEL,
            api_key=config.ZHIPUAI_API_KEY,
        )

        # 设置全局配置
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.chunk_size = config.CHUNK_SIZE
        Settings.chunk_overlap = config.CHUNK_OVERLAP

        # 初始化 Chroma 客户端
        self.chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)

        # 获取或创建集合
        self.chroma_collection = self.chroma_client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},  # 指定使用余弦相似度
        )

    def build_index(self, force_rebuild=False):
        """Build or rebuild the document index."""
        # 如果强制重建，清空现有数据
        if force_rebuild:
            print("🗑️  清空现有索引...")
            try:
                self.chroma_client.delete_collection(config.COLLECTION_NAME)
            except Exception as e:
                print(f"⚠️  删除集合时出现警告: {e}")
            self.chroma_collection = self.chroma_client.create_collection(
                config.COLLECTION_NAME
            )

        print(f"📂 从 {config.DATA_DIR} 读取文档...")
        documents = SimpleDirectoryReader(config.DATA_DIR).load_data()
        print(f"✅ 读取了 {len(documents)} 个文档")

        # 创建向量存储
        vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # 构建索引
        print("🔨 构建向量索引...")
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=True,
        )

        print(f"✅ 索引构建完成！存储在 {config.CHROMA_PERSIST_DIR}")
        print(f"📊 集合中文档数量: {self.chroma_collection.count()}")
        return index

    def add_documents(self, file_paths):
        """Add new documents to existing index."""
        print(f"📄 添加 {len(file_paths)} 个新文档...")
        # TODO: 实现增量添加逻辑
        documents = SimpleDirectoryReader(input_files=file_paths).load_data()

        vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, storage_context=storage_context
        )

        for doc in documents:
            index.insert(doc)

        print(f"✅ 成功添加 {len(documents)} 个文档")


def main():
    """Main entry point for indexing."""
    import argparse

    parser = argparse.ArgumentParser(description="Build document index")
    parser.add_argument(
        "--rebuild", action="store_true", help="Force rebuild index from scratch"
    )
    args = parser.parse_args()

    indexer = DocumentIndexer()
    indexer.build_index(force_rebuild=args.rebuild)


if __name__ == "__main__":
    main()
