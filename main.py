import time
from mlx_engine import DreamsMLXEngine
from graph_builder import SymbolGraphBuilder

def test_core():
    print("💎 DREAMS AI: M2 MAX INTELLIGENCE CORE")
    
    # Init engines
    engine = DreamsMLXEngine()
    builder = SymbolGraphBuilder("python")
    
    code = """
class DyagnosysApp:
    def start_assessment(self, user_id):
        return True

def validate_privacy_shield():
    pass
    """

    print("\n[STEP 1] Structural Analysis...")
    symbols = builder.parse_symbols(code)
    for s in symbols:
        print(f"  → Found {s['type']}: {s['name']} (Line {s['line']})")

    print("\n[STEP 2] Semantic Vectorization (Metal GPU)...")
    for s in symbols:
        start = time.time()
        _ = engine.get_embedding(s['name'])
        elapsed = (time.time() - start) * 1000
        print(f"  → Vectorized '{s['name']}' in {elapsed:.2f}ms")

    print("\n✅ DREAMS CORE OPERATIONAL")

if __name__ == "__main__":
    test_core()

