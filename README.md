# cog-core

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Apple-Silicon-000?style=for-the-badge&logo=apple" alt="Apple Silicon">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/MLX-FF6B35?style=for-the-badge" alt="MLX">
  <a href="https://opencode.cafe"><img src="https://img.shields.io/badge/OpenCode-Cafe-orange?style=for-the-badge" alt="OpenCode Cafe"></a>
</p>

<p align="center">
  <strong>Semantic code search engine using Nomic embeddings on Apple Silicon MLX</strong>
</p>

---

## What is cog-core?

**cog-core** is a semantic code search engine that uses neural embeddings to understand code by meaning. Built on Apple Silicon's MLX framework with Metal GPU acceleration, it provides fast, local vector search for your codebase.

### Why cog-core?

Traditional code search finds exact text matches. cog-core understands **what code does**, not just **what it says**.

| Search Type     | Example Query                  | Result                                              |
| --------------- | ------------------------------ | --------------------------------------------------- |
| **Traditional** | "find `login` function"        | Files containing "login"                            |
| **cog-core**    | "find authentication handling" | All auth-related code: login, validate, permissions |

### Performance

| Operation             | Time (M2 Max) |
| --------------------- | ------------- |
| Embed single function | ~5ms          |
| Index 1000 symbols    | ~5s           |
| Semantic search       | ~10ms         |

---

## Key Features

- 🧠 **Neural Embeddings** - Nomic embed model via MLX on Metal GPU
- 🌳 **Code Analysis** - Tree-sitter symbol extraction and dependency graphs
- 📊 **Vector Database** - LanceDB for semantic code search (RAG)
- 🔗 **Dependency Graphs** - NetworkX-powered code dependency visualization
- 🚀 **Apple Silicon Optimized** - Native M1/M2/M3 GPU acceleration

---

## Installation

### Prerequisites

- macOS with Apple Silicon (M1/M2/M3)
- Python 3.12+
- Xcode command line tools

### Quick Install

```bash
# Clone the repository
git clone https://github.com/vitorcalvi/cog-core.git
cd cog-core

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

---

## Quick Start

### Python API

```python
from mlx_engine import DreamsMLXEngine
from graph_builder import SymbolGraphBuilder

# Initialize engines
engine = DreamsMLXEngine()
builder = SymbolGraphBuilder("python")

# Parse code structure
code = """
class MyApp:
    def process_data(self, input_data):
        return transform(input_data)

def transform(data):
    return data.upper()
"""

symbols = builder.parse_symbols(code)
for s in symbols:
    print(f"Found {s['type']}: {s['name']}")

# Generate semantic embeddings
embedding = engine.get_embedding("data processing function")
print(f"Embedding dimension: {len(embedding)}")
```

### Index Your Codebase

```bash
# Index the current directory
python indexer.py
```

---

## Components

### DreamsMLXEngine

Generates neural embeddings using MLX on Apple Silicon GPU:

```python
from mlx_engine import DreamsMLXEngine

engine = DreamsMLXEngine()

# Generate embedding for semantic search
embedding = engine.get_embedding("authentication handler")
```

**Model**: [nomic-ai/nomic-embed-text-v1.5](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)

### SymbolGraphBuilder

Extracts code symbols and builds dependency graphs:

```python
from graph_builder import SymbolGraphBuilder

builder = SymbolGraphBuilder("python")

# Parse symbols from code
symbols = builder.parse_symbols(code)
# [{'name': 'MyClass', 'type': 'class', 'line': 3}, ...]

# Build dependency graph
builder.extract_resource_dependencies(symbols, code)
graph = builder.build_dependency_graph()

# Visualize
builder.visualize_graph("dependency_graph.png")
```

### Code Indexer

Vectorize your codebase for semantic search:

```python
from indexer import index_codebase

# Index current directory
index_codebase()
```

Or via CLI:

```bash
python indexer.py
```

---

## Project Structure

```
cog-core/
├── mlx_engine.py          # Metal GPU embedding generation
├── graph_builder.py       # Tree-sitter symbol extraction
├── indexer.py             # Codebase vectorization pipeline
├── main.py                # Demo entry point
├── test_resource_deps.py  # Tests
├── dreams_memory/         # LanceDB vector database (generated)
├── AGENTS.md              # Development guidelines
├── pyproject.toml         # Dependencies
└── README.md              # This file
```

---

## Requirements

- macOS with Apple Silicon (M1/M2/M3)
- Python 3.12+
- Xcode command line tools (`xcode-select --install`)

---

## Dependencies

| Library                     | Purpose                                       | Documentation                                                                    |
| --------------------------- | --------------------------------------------- | -------------------------------------------------------------------------------- |
| `mlx`                       | Apple Silicon ML framework (M2 Max Metal GPU) | [mlx.ai](https://mlx.ai)                                                         |
| `mlx-lm`                    | Language model utilities                      | [GitHub](https://github.com/ml-explore/mlx)                                      |
| `sentence-transformers`     | Nomic embed model (MPS backend)               | [sbert.net](https://www.sbert.net)                                               |
| `tree-sitter`               | Code parsing and symbol extraction            | [tree-sitter.org](https://tree-sitter.org)                                       |
| `tree-sitter-language-pack` | Language support                              | [GitHub](https://github.com/s得不到ter-language-packs/tree-sitter-language-pack) |
| `networkx`                  | Dependency graph construction and analysis    | [networkx.org](https://networkx.org)                                             |
| `lancedb`                   | Vector database for code embeddings           | [lancedb.com](https://lancedb.com)                                               |
| `matplotlib`                | Graph visualization                           | [matplotlib.org](https://matplotlib.org)                                         |

---

## Testing

```bash
# Run all tests
python test_resource_deps.py

# Run specific test
python -c "from test_resource_deps import test_resource_dependencies; test_resource_dependencies()"
```

---

## How It Works

1. **Code Parsing** - Tree-sitter extracts functions, classes from source
2. **Embedding Generation** - Nomic model converts code to vectors on Metal GPU
3. **Vector Storage** - LanceDB stores embeddings for fast similarity search
4. **Semantic Query** - Query embedded, compared against stored vectors
5. **Results** - Top matching code snippets returned by similarity score

---

## Related Projects

| Project              | Description                          | Link                                                                 |
| -------------------- | ------------------------------------ | -------------------------------------------------------------------- |
| **cog-mcp**          | MCP Server wrapper for AI assistants | [GitHub](https://github.com/vitorcalvi/cog-mcp)                      |
| **OpenCode Cafe**    | MCP server marketplace               | [opencode.cafe](https://www.opencode.cafe)                           |
| **Nomic Embed Text** | Embedding model used                 | [HuggingFace](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) |

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with ⚙️ by <a href="https://github.com/vitorcalvi">vitorcalvi</a>
</p>
