import os
import lancedb
import time
from graph_builder import SymbolGraphBuilder
from mlx_engine import DreamsMLXEngine

# CONFIG
DB_PATH = "./dreams_memory"
TARGET_DIR = "."  # Index the current directory

def index_codebase():
    print(f"🚀 DREAMS AI: Starting M2 Matrix Indexing on {TARGET_DIR}...")
    
    # 1. Initialize Engines
    engine = DreamsMLXEngine()
    builder = SymbolGraphBuilder()
    
    # 2. Connect to Local DB
    db = lancedb.connect(DB_PATH)
    
    # Define Schema: filename, symbol_name, code_snippet, vector
    data = []
    
    # 3. Walk and Crunch
    start_time = time.time()
    count = 0
    
    for root, _, files in os.walk(TARGET_DIR):
        if "venv" in root or "__pycache__" in root or ".git" in root:
            continue
            
        for file in files:
            if not file.endswith(".py"): continue
            
            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Extract Functions/Classes to chunk intelligently
            symbols = builder.parse_symbols(content)
            
            # If no symbols, index whole file as one chunk
            if not symbols:
                vector = engine.get_embedding(content)
                data.append({
                    "filename": file,
                    "path": filepath,
                    "symbol": "file",
                    "text": content,
                    "vector": vector
                })
                count += 1
                continue

            # Index specific symbols
            lines = content.split('\n')
            for sym in symbols:
                # Naive chunking: grab line number to line number + 20 (or until next symbol)
                # For robust chunking, you'd use exact byte ranges, but this works for v1
                s_line = sym['line'] - 1
                chunk = "\n".join(lines[s_line:s_line+30]) # Capture ~30 lines of context
                
                vector = engine.get_embedding(chunk)
                data.append({
                    "filename": file,
                    "path": filepath,
                    "symbol": sym['name'],
                    "text": chunk,
                    "vector": vector
                })
                print(f"  → Embedded {sym['type']}: {sym['name']}")
                count += 1

    # 4. Save to Disk
        # 4. Save to Disk
    if data:
        # Create or Overwrite table
        tbl = db.create_table("codebase", data, mode="overwrite")
        elapsed = time.time() - start_time
        print(f"✅ Indexed {count} symbols in {elapsed:.2f}s using Metal GPU.")
        
        # Only train index if we have enough data (requires >256 vectors)
        if count > 256:
            print("  → Optimizing Vector Index (IVF-PQ)...")
            tbl.create_index(metric="cosine")
        else:
            print("  → Dataset small (<256), using high-precision Flat Search (No Index needed).")


if __name__ == "__main__":
    index_codebase()

