# RAG 服务快速开始指南

> 5 分钟快速搭建你的第一个 RAG（检索增强生成）服务

## 🚀 快速开始（5 步）

### 第 1 步：安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 第 2 步：配置 API Key

创建 `.env` 文件：

```bash
echo "ZHIPUAI_API_KEY=your_api_key_here" > .env
```

> 💡 从 [智谱AI开放平台](https://open.bigmodel.cn/) 获取 API Key

### 第 3 步：准备文档

```bash
# 创建数据目录
mkdir -p data

# 添加你的文档（支持 txt, pdf, docx, md 等格式）
# 例如：
echo "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。" > data/ai_intro.txt
echo "机器学习是人工智能的一个子集，它使计算机能够从数据中学习并改进，而无需明确编程。" > data/ml_basics.txt
```

### 第 4 步：构建索引

```bash
python indexer.py
```

预期输出：
```
📂 从 ./data 读取文档...
✅ 读取了 2 个文档
🔨 构建向量索引...
✅ 索引构建完成！存储在 ./chroma_db
📊 集合中文档数量: 8
```

### 第 5 步：开始查询

**选项 A：交互式命令行**

```bash
python query_service.py
```

然后输入你的问题：
```
❓ 请输入问题: 什么是人工智能？
```

**选项 B：启动 API 服务**

```bash
python api.py
```

访问 http://localhost:8000/docs 查看 API 文档

**选项 C：运行示例**

```bash
python example_usage.py
```

## 📝 快速测试

使用 curl 测试 API：

```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "什么是机器学习？", "return_sources": true}'
```

## 🔍 验证安装

运行验证脚本检查所有组件：

```bash
python verify_setup.py
```

## 📚 常用命令

| 命令 | 说明 |
|------|------|
| `python indexer.py` | 构建/更新索引 |
| `python indexer.py --rebuild` | 强制重建索引 |
| `python query_service.py` | 交互式查询 |
| `python api.py` | 启动 API 服务 |
| `python example_usage.py` | 运行示例 |
| `python verify_setup.py` | 验证安装 |

## 🆚 对比：原始版本 vs 增强版本

### 原始 `starter.py`
```python
# 每次运行都要重建索引（慢）
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# 只能运行一次查询
response = query_engine.query("What is this document about?")
```

### 增强版本
```python
# 第一次：构建索引（只需一次）
python indexer.py

# 之后：快速查询（无需重建索引）
python query_service.py  # 或 python api.py
```

**优势：**
- ✅ 索引持久化，无需每次重建
- ✅ 可以多次查询，响应快速
- ✅ 支持 REST API 访问
- ✅ 生产环境就绪

## 🎯 使用场景示例

### 场景 1：文档问答系统

```bash
# 1. 添加公司文档
cp company_docs/* data/

# 2. 构建索引
python indexer.py

# 3. 启动 API
python api.py

# 4. 员工可以通过 API 查询
curl -X POST "http://localhost:8000/query" \
     -d '{"question": "公司的休假政策是什么？"}'
```

### 场景 2：知识库搜索

```bash
# 1. 添加技术文档
cp technical_docs/* data/

# 2. 构建索引
python indexer.py

# 3. 交互式搜索
python query_service.py
```

### 场景 3：研究论文分析

```python
# 使用 Python 脚本
from query_service import QueryService

service = QueryService()

questions = [
    "这篇论文的主要贡献是什么？",
    "使用了哪些方法？",
    "实验结果如何？"
]

for q in questions:
    result = service.query(q)
    print(f"Q: {q}")
    print(f"A: {result['answer']}\n")
```

## ⚡ 性能优化

### 如果查询太慢：

**调整 `config.py`：**
```python
SIMILARITY_TOP_K = 2      # 减少检索数量（默认是 3）
CHUNK_SIZE = 256          # 减小文档块大小（默认是 512）
```

### 如果回答质量不够好：

**调整 `config.py`：**
```python
SIMILARITY_TOP_K = 5      # 增加检索数量
CHUNK_SIZE = 1024         # 增大文档块大小
CHUNK_OVERLAP = 100       # 增加重叠（默认是 50）
```

## 🔧 故障排除

### 问题 1：`RuntimeError: 未找到索引`

**解决方案：**
```bash
python indexer.py
```

### 问题 2：API Key 错误

**解决方案：**
检查 `.env` 文件中的 `ZHIPUAI_API_KEY` 是否正确

### 问题 3：没有文档

**解决方案：**
```bash
# 检查 data 目录
ls data/

# 添加文档
cp your_docs/* data/
```

### 问题 4：依赖缺失

**解决方案：**
```bash
uv sync  # 或 pip install -e .
```

## 📖 下一步

- 📚 阅读完整文档：[RAG_SERVICE_README.md](RAG_SERVICE_README.md)
- 🧪 运行所有示例：`python example_usage.py`
- 🔍 查看 API 文档：http://localhost:8000/docs（先启动 API）
- 🛠️ 自定义配置：修改 `config.py`

## 💡 提示

1. **索引只需构建一次**，除非文档更新
2. **使用 `--rebuild`** 当文档变更后重建索引
3. **API 服务**可以同时处理多个查询
4. **查看源码**了解更多自定义选项

## 🤝 获取帮助

- 遇到问题？运行 `python verify_setup.py` 诊断
- 查看示例：`python example_usage.py`
- 阅读详细文档：`RAG_SERVICE_README.md`

---

**恭喜！🎉 你已经成功搭建了一个 RAG 服务！**