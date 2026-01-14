"""Example usage script demonstrating the enhanced RAG workflow."""

import os
import sys
from pathlib import Path

# Ensure imports work from this directory
sys.path.insert(0, str(Path(__file__).parent))

import config
from indexer import DocumentIndexer
from query_service import QueryService


def example_1_build_index():
    """Example 1: Build index from documents."""
    print("\n" + "=" * 70)
    print("示例 1: 构建索引")
    print("=" * 70)

    # 检查 data 目录
    if not os.path.exists(config.DATA_DIR):
        print(f"❌ 错误: 未找到 {config.DATA_DIR} 目录")
        print(f"请创建目录并添加文档: mkdir {config.DATA_DIR}")
        return

    # 检查是否有文档
    data_path = Path(config.DATA_DIR)
    files = list(data_path.glob("*"))
    if not files:
        print(f"❌ 错误: {config.DATA_DIR} 目录为空")
        print("请添加一些文档（txt, pdf, md 等格式）")
        return

    print(f"📁 找到 {len(files)} 个文件")

    # 创建索引器并构建索引
    indexer = DocumentIndexer()
    indexer.build_index(force_rebuild=False)

    print("\n✅ 索引构建完成！")


def example_2_simple_query():
    """Example 2: Simple query without sources."""
    print("\n" + "=" * 70)
    print("示例 2: 简单查询")
    print("=" * 70)

    try:
        # 初始化查询服务
        service = QueryService()

        # 执行查询
        question = "What is this document about?"
        print(f"\n❓ 问题: {question}")

        result = service.query(question, return_sources=False)

        print("\n💡 回答:")
        print("-" * 70)
        print(result["answer"])
        print("-" * 70)

    except RuntimeError as e:
        print(f"\n{e}")
        print("\n💡 请先运行: python indexer.py")


def example_3_query_with_sources():
    """Example 3: Query with source attribution."""
    print("\n" + "=" * 70)
    print("示例 3: 带来源的查询")
    print("=" * 70)

    try:
        service = QueryService()

        questions = [
            "What are the main topics covered?",
            "Can you summarize the key points?",
            "What is the conclusion?",
        ]

        for i, question in enumerate(questions, 1):
            print(f"\n{'─' * 70}")
            print(f"查询 {i}/{len(questions)}: {question}")
            print("─" * 70)

            result = service.query(question, return_sources=True)

            print(f"\n💡 回答: {result['answer']}")

            if result["sources"]:
                print(f"\n📚 参考了 {len(result['sources'])} 个文档片段:")
                for src in result["sources"]:
                    print(f"  • 片段 {src['chunk_id']} (相似度: {src['score']:.3f})")
                    print(f"    来源: {src['metadata'].get('file_name', 'Unknown')}")

    except RuntimeError as e:
        print(f"\n{e}")


def example_4_custom_parameters():
    """Example 4: Query with custom parameters."""
    print("\n" + "=" * 70)
    print("示例 4: 自定义查询参数")
    print("=" * 70)

    try:
        import chromadb
        from llama_index.core import Settings, VectorStoreIndex
        from llama_index.embeddings.zhipuai import ZhipuAIEmbedding
        from llama_index.llms.zhipuai import ZhipuAI
        from llama_index.vector_stores.chroma import ChromaVectorStore

        # 配置模型
        llm = ZhipuAI(model=config.LLM_MODEL, api_key=config.ZHIPUAI_API_KEY)
        embed_model = ZhipuAIEmbedding(
            model=config.EMBEDDING_MODEL, api_key=config.ZHIPUAI_API_KEY
        )

        Settings.llm = llm
        Settings.embed_model = embed_model

        # 加载索引
        chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
        chroma_collection = chroma_client.get_collection(name=config.COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, embed_model=embed_model
        )

        # 创建自定义查询引擎
        query_engine = index.as_query_engine(
            similarity_top_k=5,  # 检索 Top-5 而不是默认的 3
            response_mode="tree_summarize",  # 使用树形摘要模式
            verbose=True,
        )

        question = "What are all the important details?"
        print(f"\n❓ 问题: {question}")
        print(f"📊 参数: top_k=5, response_mode=tree_summarize")

        response = query_engine.query(question)

        print("\n💡 回答:")
        print("-" * 70)
        print(response)

    except Exception as e:
        print(f"\n❌ 错误: {e}")


def example_5_batch_queries():
    """Example 5: Batch query processing."""
    print("\n" + "=" * 70)
    print("示例 5: 批量查询处理")
    print("=" * 70)

    try:
        service = QueryService()

        # 批量问题
        questions = [
            "What is the main topic?",
            "Who are the key people mentioned?",
            "What are the important dates?",
            "What are the conclusions?",
        ]

        results = []

        print(f"\n🔄 处理 {len(questions)} 个查询...\n")

        for i, question in enumerate(questions, 1):
            print(f"[{i}/{len(questions)}] 处理中...", end=" ")
            result = service.query(question, return_sources=False)
            results.append({"question": question, "answer": result["answer"]})
            print("✅")

        # 显示结果
        print("\n" + "=" * 70)
        print("📊 批量查询结果")
        print("=" * 70)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['question']}")
            print(f"   → {result['answer'][:100]}...")

    except RuntimeError as e:
        print(f"\n{e}")


def example_6_error_handling():
    """Example 6: Proper error handling."""
    print("\n" + "=" * 70)
    print("示例 6: 错误处理")
    print("=" * 70)

    # 测试各种错误情况

    # 1. 索引不存在
    print("\n1️⃣ 测试: 索引不存在的情况")
    try:
        service = QueryService()
        print("   ✅ 索引加载成功")
    except RuntimeError as e:
        print(f"   ⚠️  预期错误: {str(e)[:50]}...")

    # 2. 空查询
    print("\n2️⃣ 测试: 空查询")
    try:
        service = QueryService()
        empty_query = ""
        if not empty_query.strip():
            print("   ✅ 正确检测到空查询")
        else:
            result = service.query(empty_query)
    except Exception as e:
        print(f"   ❌ 错误: {e}")

    # 3. API Key 缺失
    print("\n3️⃣ 测试: API Key 检查")
    if not config.ZHIPUAI_API_KEY:
        print("   ⚠️  警告: ZHIPUAI_API_KEY 未设置")
        print("   请在 .env 文件中设置 ZHIPUAI_API_KEY")
    else:
        print("   ✅ API Key 已配置")


def example_7_performance_test():
    """Example 7: Simple performance test."""
    print("\n" + "=" * 70)
    print("示例 7: 性能测试")
    print("=" * 70)

    try:
        import time

        service = QueryService()

        test_questions = [
            "What is this about?",
            "Summarize the main points.",
            "What are the conclusions?",
        ]

        print(f"\n⏱️  测试 {len(test_questions)} 个查询的性能...\n")

        times = []
        for i, question in enumerate(test_questions, 1):
            start_time = time.time()
            result = service.query(question, return_sources=True)
            elapsed = time.time() - start_time
            times.append(elapsed)

            print(f"查询 {i}: {elapsed:.2f} 秒")
            print(f"  - 检索到 {len(result['sources'])} 个相关片段")
            print(f"  - 回答长度: {len(result['answer'])} 字符")

        print(f"\n📊 统计:")
        print(f"  - 平均响应时间: {sum(times) / len(times):.2f} 秒")
        print(f"  - 最快: {min(times):.2f} 秒")
        print(f"  - 最慢: {max(times):.2f} 秒")

    except RuntimeError as e:
        print(f"\n{e}")


def main():
    """Main function to run all examples."""
    print("\n" + "=" * 70)
    print("🚀 RAG 服务使用示例")
    print("=" * 70)

    examples = {
        "1": ("构建索引", example_1_build_index),
        "2": ("简单查询", example_2_simple_query),
        "3": ("带来源的查询", example_3_query_with_sources),
        "4": ("自定义参数", example_4_custom_parameters),
        "5": ("批量查询", example_5_batch_queries),
        "6": ("错误处理", example_6_error_handling),
        "7": ("性能测试", example_7_performance_test),
        "all": ("运行所有示例", None),
    }

    print("\n可用示例:")
    for key, (desc, _) in examples.items():
        print(f"  {key}. {desc}")

    choice = input("\n请选择示例 (1-7 或 'all'): ").strip()

    if choice == "all":
        # 运行所有示例
        for key in ["1", "2", "3", "4", "5", "6", "7"]:
            examples[key][1]()
            input("\n按 Enter 继续下一个示例...")
    elif choice in examples and examples[choice][1] is not None:
        examples[choice][1]()
    else:
        print("❌ 无效选择")
        return

    print("\n" + "=" * 70)
    print("✅ 示例完成！")
    print("=" * 70)
    print("\n💡 提示:")
    print("  - 查看 RAG_SERVICE_README.md 了解更多详情")
    print("  - 运行 'python api.py' 启动 REST API 服务")
    print("  - 运行 'python query_service.py' 进入交互式查询")
    print()


if __name__ == "__main__":
    main()
