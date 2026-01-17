# AGENTS.md

This document provides guidelines for AI coding agents working with the **cog-core** repository.

## Project Overview

cog-core is a Python-based semantic code search engine that uses neural embeddings (Nomic) on Apple Silicon MLX with Metal GPU acceleration. It provides vector search capabilities for code intelligence applications.

## Build / Lint / Test Commands

### Dependencies & Environment

```bash
# Install dependencies (project uses uv for package management)
uv pip install -e .

# Python version requirement
python >= 3.12

# Verify installation
python -c "from mlx_engine import DreamsMLXEngine; print('OK')"
```

### Running Code

```bash
# Run main entry point (demo)
python main.py

# Run indexer (codebase vectorization)
python indexer.py

# Run specific test
python test_resource_deps.py

# Run individual test function (for debugging)
python -c "from test_resource_deps import test_resource_dependencies; test_resource_dependencies()"
```

### Test Framework

- Tests are standalone Python scripts (not pytest/unittest)
- Run tests directly: `python test_file.py`
- Tests print output with `print()` statements and exit silently

## Code Style Guidelines

### Imports

- **Order**: Standard library → Third-party → Local modules
- **Format**: Sorted alphabetically within each group
- **Example**:

  ```python
  import os
  import re
  from collections import defaultdict

  import networkx as nx
  import tree_sitter

  from mlx_engine import DreamsMLXEngine
  ```

### Naming Conventions

| Type            | Convention       | Example                              |
| --------------- | ---------------- | ------------------------------------ |
| Variables       | snake_case       | `resource_dependencies`              |
| Functions       | snake_case       | `parse_symbols()`                    |
| Classes         | PascalCase       | `SymbolGraphBuilder`                 |
| Constants       | UPPER_SNAKE_CASE | `DB_PATH`                            |
| Private methods | prefix with `_`  | `_extract_resources_from_function()` |

### Type Hints (Recommended)

- Use type hints for function signatures when clear
- Avoid `Any` when possible
- Example:

  ```python
  def parse_symbols(self, code: str) -> list[dict[str, str]]:
      ...
  ```

### Formatting

- **Line length**: ~88 characters (standard Python convention)
- **Indentation**: 4 spaces (no tabs)
- **F-strings**: Preferred for string formatting
- **Line breaks**: Use parentheses for multi-line expressions

### Docstrings

- Use triple double quotes `"""`
- Include Args and Returns sections for non-trivial functions
- Example:

  ```python
  def extract_resource_dependencies(self, symbols: list, code: str) -> tuple[dict, dict]:
      """
      Extract resource dependencies from operations.

      Args:
          symbols: List of extracted symbols from parse_symbols
          code: The source code to analyze

      Returns:
          Tuple of (resource_deps, op_resources)
      """
  ```

### Error Handling

- Use specific exception types when possible
- Let exceptions propagate for unrecoverable errors
- Add context in error messages when helpful
- Example:

  ```python
  try:
      with open(filepath, "r", encoding="utf-8") as f:
          content = f.read()
  except FileNotFoundError:
      print(f"Warning: File not found: {filepath}")
      continue
  ```

## Code Patterns

### Graph operations

Use NetworkX `DiGraph` for dependency graphs:

```python
import networkx as nx

G = nx.DiGraph()
G.add_node("function_name", type="operation")
G.add_node("resource_name", type="resource")
G.add_edge("function_name", "resource_name", relation="uses")
```

### Tree-sitter

Handle both query cursor API styles (0.21 and 0.23+):

```python
import tree_sitter
from tree_sitter_language_pack import get_language, get_parser

parser = get_parser("python")

try:
    # 0.23+ style
    cursor = tree_sitter.QueryCursor(query)
    results = cursor.captures(tree.root_node)
except TypeError:
    # 0.21 style
    cursor = tree_sitter.QueryCursor()
    results = cursor.captures(query, tree.root_node)
```

### MPS/GPU

Use `device="mps"` for Metal GPU offloading:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "nomic-ai/nomic-embed-text-v1.5",
    device="mps"  # Metal Performance Shaders
)
```

### Vector storage

Use LanceDB with IVF-PQ index for large datasets:

```python
import lancedb

db = lancedb.connect("./dreams_memory")
tbl = db.create_table("codebase", data, mode="overwrite")

# For large datasets (>256 vectors)
tbl.create_index(metric="cosine")
```

## Project Structure

```
cog-core/
├── main.py              # Entry point with DreamsMLXEngine demo
├── indexer.py           # Codebase vectorization pipeline
├── graph_builder.py     # Symbol extraction & dependency analysis
├── mlx_engine.py        # Metal GPU embedding generation
├── test_resource_deps.py # Resource dependency tests
├── dreams_memory/       # LanceDB vector database (generated)
├── AGENTS.md            # Development guidelines
├── pyproject.toml       # Dependencies
└── README.md            # User documentation
```

## Key Libraries

| Library                 | Purpose                                       | Documentation                              |
| ----------------------- | --------------------------------------------- | ------------------------------------------ |
| `mlx`                   | Apple Silicon ML framework (M2 Max Metal GPU) | [mlx.ai](https://mlx.ai)                   |
| `tree-sitter`           | Code parsing and symbol extraction            | [tree-sitter.org](https://tree-sitter.org) |
| `networkx`              | Dependency graph construction                 | [networkx.org](https://networkx.org)       |
| `lancedb`               | Vector database for code embeddings           | [lancedb.com](https://lancedb.com)         |
| `sentence-transformers` | Nomic embed model for text vectorization      | [sbert.net](https://www.sbert.net)         |

## Common Tasks

### Adding a New Language

1. Install language pack: `tree-sitter-language-pack`
2. Update parser initialization:

   ```python
   from tree_sitter_language_pack import get_parser

   builder = SymbolGraphBuilder("javascript")
   ```

3. Update tree-sitter queries in `parse_symbols()` if needed

### Modifying Embedding Model

In `mlx_engine.py`:

```python
class DreamsMLXEngine:
    def __init__(self, model_path="nomic-ai/nomic-embed-text-v1.5"):
        self.model = SentenceTransformer(model_path, device="mps")
```

### Customizing Indexing

In `indexer.py`, modify the `index_codebase()` function to:

- Change file extensions to index
- Adjust chunk size
- Add filtering rules

## Testing

### Running Tests

```bash
# Run all tests
python test_resource_deps.py

# Verbose output
python -v test_resource_deps.py
```

### Writing Tests

Tests should be standalone scripts that:

1. Set up test fixtures
2. Run the function/component
3. Print results
4. Exit silently (no assertion errors = pass)

Example:

```python
def test_my_feature():
    # Setup
    input_data = "test code"

    # Execute
    result = process(input_data)

    # Verify
    assert result is not None
    print(f"✓ Test passed: {result}")

if __name__ == "__main__":
    test_my_feature()
```

## Debugging

### Common Issues

| Issue                    | Solution                             |
| ------------------------ | ------------------------------------ |
| MLX not available        | Ensure macOS + Apple Silicon         |
| MPS backend fails        | Check Metal GPU availability         |
| Tree-sitter parse errors | Verify language pack installed       |
| LanceDB errors           | Delete `dreams_memory/` and re-index |

### Debug Output

Add print statements for debugging:

```python
def parse_symbols(self, code):
    print(f"[DEBUG] Parsing {len(code)} chars...")
    # ... logic
    print(f"[DEBUG] Found {len(symbols)} symbols")
    return symbols
```

## Best Practices

1. **Use type hints** - Improves code clarity and IDE support
2. **Handle MPS fallbacks** - Some operations may not support Metal
3. **Optimize chunk sizes** - Balance memory usage and search quality
4. **Test on real codebases** - Synthetic tests may miss edge cases
5. **Profile on M2 Max** - Performance characteristics differ from CPU

## Related Documentation

- [cog-mcp README](https://github.com/vitorcalvi/cog-mcp)
- [MLX Documentation](https://mlx.readthedocs.io)
- [Nomic Embeddings](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)
- [OpenCode Cafe](https://www.opencode.cafe)
