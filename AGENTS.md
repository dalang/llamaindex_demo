# AGENTS.md - Agent Guidelines for LlamaIndex Demo

## Project Overview

Python 3.13 demo project using LlamaIndex for RAG. Minimal codebase with single entry point (`main.py`).

## Commands

### Setup & Run
```bash
uv venv                              # Create virtual environment
source .venv/bin/activate           # Activate (optional)
uv pip install -e .                  # Install dependencies
uv run python main.py                # Run main script
uv run python -m pytest              # Run tests with uv
```

### Testing (pytest)
```bash
uv pip install pytest pytest-cov    # Install test tools
uv run pytest                        # All tests
uv run pytest tests/test_module.py  # Single file
uv run pytest tests/test_module.py::test_function  # Specific test
uv run pytest --cov=.               # With coverage
```

### Linting & Formatting (ruff)
```bash
uv pip install ruff                 # Install linting tools
uv run ruff check . && ruff format . # Lint + format
uv run ruff check --fix .           # Auto-fix issues
```

### Type Checking (mypy)
```bash
uv pip install mypy                  # Install type checker
uv run mypy .
```

## Code Style

**Python 3.13+**: Use modern features (type hints, f-strings, context managers)

**Imports**: Standard → third-party → local, separated by blank lines
```python
import os
from typing import Optional

from llama_index.core import VectorStoreIndex
from llama_index.core.readers import SimpleDirectoryReader

from .utils import helper_function
```

**Type Hints**: Add to all functions
```python
def process(docs: List[str], config: Optional[Dict] = None) -> Dict:
    pass
```

**Naming**: `snake_case` for variables/functions, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants

**Error Handling**: Specific exceptions only, meaningful messages
```python
try:
    Path(file_path).read_text()
except FileNotFoundError:
    raise ValueError(f"Document not found: {file_path}")
```

**LlamaIndex Patterns**:
```python
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.readers import SimpleDirectoryReader

Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
response = index.as_query_engine().query("What is X?")
```

**Logging**: Use `logging` module, not `print()`
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Processing {len(items)} items")
```

**Docstrings**: Google-style with Args/Returns/Raises

## Structure

```
llamaindex_demo/
├── data/          # Source documents
├── tests/         # pytest files
├── src/llamaindex_demo/  # Package code
├── main.py
├── pyproject.toml
└── AGENTS.md
```

## Key Notes

1. **Python-only**: No TypeScript
2. **Minimal patterns**: Establish sensible best practices
3. **LlamaIndex focus**: Prioritize library idioms
4. **Data in `/data`**
5. **Use `.venv`**: Create with `uv venv`
6. **Use `uv run`**: Execute Python commands via `uv run python` or `uv run <module>`
7. **Python 3.13 features OK**

## Pre-commit (recommended)
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```
