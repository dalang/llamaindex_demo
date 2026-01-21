# Rerank 集成指南

本指南说明如何使用本地 TEI (Text Embeddings Inference) 服务进行文档重排序（Rerank）。

## 架构概览

```
查询流程：
用户查询 → Embedding 检索 (Top 10) → TEI Rerank (Top 3) → LLM 生成答案
```

## 文件说明

### 新增文件

1. **`reranker.py`** - 自定义 TEI Reranker 实现
   - `TEIReranker` 类：通过 HTTP API 调用本地 rerank 服务
   - 自动健康检查和错误处理
   - 支持回退到原始检索结果

2. **`test_rerank.py`** - Rerank 功能测试脚本
   - 测试 TEI API 连接
   - 验证 rerank 功能是否正常

3. **`RERANK_GUIDE.md`** - 本文档

### 修改文件

1. **`config.py`** - 添加 rerank 配置
   ```python
   USE_RERANK = True
   RERANK_API_URL = "http://localhost:8099"
   RERANK_TOP_N = 3
   RERANK_TIMEOUT = 30
   SIMILARITY_TOP_K = 10  # 从 3 增加到 10
   ```

2. **`query_service.py`** - 集成 rerank 功能
   - 添加 `_setup_postprocessors()` 方法
   - 集成 `TEIReranker` 到查询引擎
   - 添加日志记录

3. **`pyproject.toml`** - 添加依赖
   ```toml
   "requests>=2.31.0",
   ```

## 快速开始

### 1. 验证 TEI 服务

```bash
# 测试健康检查
curl http://localhost:8099/health

# 测试 rerank API
curl -X POST http://localhost:8099/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是 RAG？",
    "texts": [
      "RAG 是检索增强生成的缩写",
      "今天天气很好",
      "RAG 结合了检索和生成"
    ]
  }'

# 预期输出：
# [
#   {"index": 0, "score": 0.95},
#   {"index": 2, "score": 0.85},
#   {"index": 1, "score": 0.15}
# ]
```

### 3. 测试 Rerank 功能

```bash
# 运行测试脚本
uv run python test_rerank.py
```

预期输出：
```
🧪 测试 TEI Reranker
✅ TEI Rerank API 连接成功: http://localhost:8099

查询: 什么是 RAG？

原始顺序 (3 个文档):
1. [分数: 0.8000] RAG 是检索增强生成（Retrieval-Augmented Generation）的缩写...
2. [分数: 0.7500] 今天天气很好，阳光明媚...
3. [分数: 0.7800] RAG 系统结合了检索和生成两个步骤...

Rerank 后 (Top 2):
1. [分数: 0.9531] RAG 是检索增强生成（Retrieval-Augmented Generation）的缩写...
2. [分数: 0.8942] RAG 系统结合了检索和生成两个步骤...

✅ 测试完成
```

### 4. 运行查询服务

```bash
uv run python query_service.py
```

## 配置说明

### `config.py` 中的 Rerank 配置

```python
# 是否启用 rerank（设为 False 则使用传统检索）
USE_RERANK = True

# TEI rerank API 地址
RERANK_API_URL = "http://localhost:8099"

# rerank 后返回的文档数量
RERANK_TOP_N = 3

# API 请求超时时间（秒）
RERANK_TIMEOUT = 30

# 初始检索数量（建议 10-20，rerank 会从中选出最好的）
SIMILARITY_TOP_K = 10
```

### 推荐配置

| 场景 | SIMILARITY_TOP_K | RERANK_TOP_N | 说明 |
|------|------------------|--------------|------|
| **快速响应** | 5 | 2 | 最快，适合简单查询 |
| **平衡模式** | 10 | 3 | 推荐配置 |
| **高质量** | 20 | 5 | 最好效果，稍慢 |

## 工作原理

### 1. 传统检索（无 Rerank）

```
查询 → Embedding → 余弦相似度 → Top 3 文档 → LLM 生成
```

**问题**：
- 仅基于语义相似度
- 可能检索到语义相关但不直接回答问题的文档

### 2. 带 Rerank 的检索

```
查询 → Embedding → 余弦相似度 → Top 10 候选
     ↓
     Cross-Encoder Rerank → Top 3 最相关
     ↓
     LLM 生成精确答案
```

**优势**：
- Cross-Encoder 对查询和文档进行细粒度评分
- 更准确地识别真正相关的文档
- 通常提升 10-30% 的检索准确率

### 3. Rerank 评分差异

**Embedding 相似度**：独立计算查询和文档的向量，然后计算余弦相似度
- 速度快
- 适合大规模初筛

**Cross-Encoder Rerank**：同时输入查询和文档，计算匹配分数
- 更准确
- 计算密集，适合小规模精排

## API 接口

### TEI Rerank API

**端点**: `POST /rerank`

**请求**:
```json
{
  "query": "什么是 RAG？",
  "texts": [
    "文档1内容",
    "文档2内容",
    "文档3内容"
  ],
  "truncate": true
}
```

**响应**:
```json
[
  {"index": 0, "score": 0.9531},
  {"index": 2, "score": 0.8942},
  {"index": 1, "score": 0.1234}
]
```

返回结果已按 `score` 降序排列。

## 故障排除

### 问题 1: 无法连接到 TEI API

**症状**:
```
⚠️  无法连接到 TEI API (http://localhost:8099): Connection refused
```

**解决方案**:
1. 确认 TEI 服务正在运行：`curl http://localhost:8099/health`
2. 检查端口是否正确
3. 如果使用 Docker，确认容器正在运行：`docker ps`

### 问题 2: Rerank 请求超时

**症状**:
```
❌ TEI Rerank API 调用失败: timeout
```

**解决方案**:
1. 增加超时时间：`RERANK_TIMEOUT = 60`
2. 减少初始检索数量：`SIMILARITY_TOP_K = 5`
3. 检查 TEI 服务是否过载

### 问题 3: 回退到原始检索

**症状**:
```
⚠️  回退到原始检索结果
```

**说明**: 这是正常的故障保护机制
- Rerank 失败时自动回退
- 系统继续使用传统检索
- 不会导致查询失败

**解决方案**: 检查 TEI 服务日志找出根本原因

## 性能优化

### 1. 调整检索参数

```python
# 场景：文档库很大（>10000 文档）
SIMILARITY_TOP_K = 20  # 增加候选数量
RERANK_TOP_N = 5       # 增加最终返回数量

# 场景：响应速度优先
SIMILARITY_TOP_K = 5
RERANK_TOP_N = 2
```

### 2. 使用 GPU 加速

TEI 支持 GPU 加速，显著提升 rerank 速度：

```bash
docker run --gpus all -p 8099:80 \
  -v $HOME/.cache/huggingface:/data \
  ghcr.io/huggingface/text-embeddings-inference:1.2 \
  --model-id cross-encoder/ms-marco-MiniLM-L-6-v2
```

### 3. 批量处理

TEI 自动支持批量处理，无需额外配置。

## 模型选择

### 当前使用的模型

```
cross-encoder/ms-marco-MiniLM-L-6-v2
- 大小: ~80MB
- 速度: 快
- 语言: 主要为英文训练，但对中文有一定支持
```

### 其他推荐模型

#### 多语言支持更好
```bash
# BAAI BGE Reranker (中文优化)
--model-id BAAI/bge-reranker-base

# 或更大的版本
--model-id BAAI/bge-reranker-large
```

#### 更小更快
```bash
--model-id cross-encoder/ms-marco-TinyBERT-L-2-v2
```

#### 更大更准确
```bash
--model-id cross-encoder/ms-marco-MiniLM-L-12-v2
```

## 监控和日志

### 查看 Rerank 日志

```python
import logging
logging.basicConfig(level=logging.INFO)
```

日志输出示例：
```
✅ TEI Rerank API 连接成功: http://localhost:8099
✅ TEI Rerank 启用: http://localhost:8099, 初始检索=10, rerank后=3
🔍 查询: 什么是 RAG？
🎯 Rerank 完成: 10 → 3 个文档
```

### 性能指标

在 `reranker.py` 中添加性能监控：

```python
import time

def _postprocess_nodes(self, nodes, query_bundle):
    start_time = time.time()
    # ... rerank 逻辑 ...
    duration = time.time() - start_time
    logger.info(f"⏱️  Rerank 耗时: {duration:.3f}s")
```

## 最佳实践

### 1. 设置合理的 Top-K

```python
# ❌ 不推荐：候选太少
SIMILARITY_TOP_K = 3
RERANK_TOP_N = 3      # rerank 没有选择空间

# ✅ 推荐：给 rerank 足够的候选
SIMILARITY_TOP_K = 10
RERANK_TOP_N = 3      # 从 10 个中选 3 个
```

### 2. 错误处理

`TEIReranker` 已内置错误处理：
- API 连接失败 → 警告并回退
- 请求超时 → 返回原始结果
- 解析错误 → 返回原始结果

### 3. 生产环境部署

```python
# 配置合理的超时
RERANK_TIMEOUT = 30  # 生产环境建议 30-60 秒

# 考虑使用负载均衡
RERANK_API_URL = "http://rerank-lb.internal:8099"

# 启用健康检查
# TEIReranker 在初始化时会自动检查
```

## 与 API 服务集成

`api.py` 中的 FastAPI 服务会自动使用 rerank：

```bash
# 启动 API 服务
uv run uvicorn api:app --reload

# 测试查询
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是 RAG？"}'
```

响应中的 `sources` 将显示 rerank 后的分数。

## 总结

✅ **优势**:
- 提升检索准确率 10-30%
- 本地部署，无需外部 API
- 自动故障回退，不影响可用性
- 低延迟（通常 < 100ms）

✅ **适用场景**:
- 需要高精度检索的应用
- 文档内容多样，语义相似度不够准确
- 对响应质量要求高的生产环境

✅ **注意事项**:
- 增加约 50-200ms 延迟（取决于硬件）
- 需要额外运行 TEI 服务
- 建议配置 GPU 以获得最佳性能

## 相关资源

- [Text Embeddings Inference (TEI) 文档](https://github.com/huggingface/text-embeddings-inference)
- [LlamaIndex Postprocessor 文档](https://docs.llamaindex.ai/en/stable/module_guides/querying/node_postprocessors/)
- [Cross-Encoder 模型](https://www.sbert.net/examples/applications/cross-encoder/README.html)
