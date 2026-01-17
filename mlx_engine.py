import mlx.core as mx
# We use sentence_transformers because it handles the specific Nomic architecture 
# better than raw MLX wrappers right now, but we run it on Metal.
from sentence_transformers import SentenceTransformer

class DreamsMLXEngine:
    def __init__(self, model_path="nomic-ai/nomic-embed-text-v1.5"):
        print(f"🚀 Initializing Nomic Embed on M2 Max...")
        # trust_remote_code=True is required for Nomic 1.5
        self.model = SentenceTransformer(model_path, trust_remote_code=True, device="mps")
        
    def get_embedding(self, text):
        """Generate embedding on Metal GPU (MPS)"""
        # Nomic specific prefix
        prefixed_text = f"search_document: {text}"
        
        # The library handles the Metal (MPS) offloading automatically when device="mps"
        embedding = self.model.encode(prefixed_text, convert_to_numpy=True)
        
        return embedding

if __name__ == "__main__":
    engine = DreamsMLXEngine()
    v = engine.get_embedding("Hello Dreams AI")
    print(f"✅ GPU Vector Generated (Dim: {len(v)})")

