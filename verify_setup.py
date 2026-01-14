"""Verification script to check if the RAG service setup is correct."""

import sys
from pathlib import Path


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("📦 检查依赖...")

    dependencies = {
        "llama_index": "LlamaIndex",
        "chromadb": "ChromaDB",
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "dotenv": "python-dotenv",
    }

    missing = []
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - 未安装")
            missing.append(name)

    if missing:
        print(f"\n⚠️  缺少依赖: {', '.join(missing)}")
        print("请运行: uv sync 或 pip install -e .")
        return False

    return True


def check_environment():
    """Check if environment variables are set."""
    print("\n🔑 检查环境变量...")

    env_file = Path(".env")
    if not env_file.exists():
        print("  ⚠️  .env 文件不存在")
        print("  创建 .env 文件并添加: ZHIPUAI_API_KEY=your_api_key")
        return False

    print("  ✅ .env 文件存在")

    # Check if API key is set
    import os

    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("ZHIPUAI_API_KEY")

    if not api_key:
        print("  ⚠️  ZHIPUAI_API_KEY 未设置")
        return False

    print(f"  ✅ ZHIPUAI_API_KEY 已设置 ({api_key[:10]}...)")
    return True


def check_data_directory():
    """Check if data directory exists and has files."""
    print("\n📁 检查数据目录...")

    data_dir = Path("data")
    if not data_dir.exists():
        print("  ⚠️  data/ 目录不存在")
        print("  创建目录: mkdir data")
        print("  然后添加文档到该目录")
        return False

    print("  ✅ data/ 目录存在")

    files = list(data_dir.glob("*"))
    if not files:
        print("  ⚠️  data/ 目录为空")
        print("  请添加文档（txt, pdf, md 等）到 data/ 目录")
        return False

    print(f"  ✅ 找到 {len(files)} 个文件")
    for f in files[:5]:  # Show first 5 files
        print(f"     - {f.name}")
    if len(files) > 5:
        print(f"     ... 还有 {len(files) - 5} 个文件")

    return True


def check_index():
    """Check if index has been built."""
    print("\n🔍 检查索引...")

    chroma_dir = Path("chroma_db")
    if not chroma_dir.exists():
        print("  ⚠️  索引未构建")
        print("  运行: python indexer.py")
        return False

    print("  ✅ 索引目录存在")

    try:
        import chromadb

        from config import CHROMA_PERSIST_DIR, COLLECTION_NAME

        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        try:
            collection = client.get_collection(COLLECTION_NAME)
            count = collection.count()
            print(f"  ✅ 索引包含 {count} 个文档片段")
            return True
        except Exception as e:
            print(f"  ⚠️  集合不存在: {e}")
            print("  运行: python indexer.py")
            return False
    except Exception as e:
        print(f"  ❌ 检查索引时出错: {e}")
        return False


def check_config():
    """Check if config file is properly set up."""
    print("\n⚙️  检查配置...")

    try:
        import config

        print("  ✅ config.py 存在")
        print(f"     - LLM Model: {config.LLM_MODEL}")
        print(f"     - Embedding Model: {config.EMBEDDING_MODEL}")
        print(f"     - Top K: {config.SIMILARITY_TOP_K}")
        print(f"     - Chunk Size: {config.CHUNK_SIZE}")
        return True
    except Exception as e:
        print(f"  ❌ 配置文件错误: {e}")
        return False


def test_query_service():
    """Test if query service can be initialized."""
    print("\n🧪 测试查询服务...")

    try:
        from query_service import QueryService

        service = QueryService()
        print("  ✅ 查询服务初始化成功")

        # Try a simple query
        print("  🔍 执行测试查询...")
        result = service.query("test", return_sources=False)
        print("  ✅ 查询执行成功")

        return True
    except RuntimeError as e:
        print(f"  ⚠️  {e}")
        return False
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False


def print_next_steps(checks):
    """Print next steps based on check results."""
    print("\n" + "=" * 70)

    if all(checks.values()):
        print("✅ 所有检查通过！系统已就绪")
        print("=" * 70)
        print("\n🎉 你可以开始使用 RAG 服务了！")
        print("\n下一步:")
        print("  1️⃣  交互式查询: python query_service.py")
        print("  2️⃣  启动 API 服务: python api.py")
        print("  3️⃣  查看示例: python example_usage.py")
        print("  4️⃣  查看文档: cat RAG_SERVICE_README.md")
    else:
        print("⚠️  部分检查未通过")
        print("=" * 70)
        print("\n需要完成以下步骤:")

        if not checks["dependencies"]:
            print("  1️⃣  安装依赖: uv sync 或 pip install -e .")

        if not checks["environment"]:
            print("  2️⃣  设置环境变量:")
            print("      - 创建 .env 文件")
            print("      - 添加: ZHIPUAI_API_KEY=your_api_key")

        if not checks["data"]:
            print("  3️⃣  准备数据:")
            print("      - mkdir data")
            print("      - 添加文档到 data/ 目录")

        if not checks["index"]:
            print("  4️⃣  构建索引: python indexer.py")

        print("\n然后重新运行: python verify_setup.py")


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("🔧 RAG 服务设置验证")
    print("=" * 70)

    checks = {
        "dependencies": check_dependencies(),
        "config": check_config(),
        "environment": check_environment(),
        "data": check_data_directory(),
        "index": check_index(),
    }

    # Only test query service if all previous checks pass
    if all(checks.values()):
        checks["query_service"] = test_query_service()
    else:
        print("\n⏭️  跳过查询服务测试（需要先完成上述步骤）")

    print_next_steps(checks)
    print()


if __name__ == "__main__":
    main()
