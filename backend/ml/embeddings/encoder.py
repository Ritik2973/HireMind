"""
This module encapsulates the pretrained Transformer model loading and encoding logic.
We use a lightweight, CPU-friendly Sentence Transformer ('all-MiniLM-L6-v2') 
to convert natural language text into rich semantic vectors (embeddings).
Model weights will be downloaded from HuggingFace on first initialization and cached locally,
avoiding the need for external API keys and ensuring deterministic inference.
"""
import numpy as np

# A global variable to cache the loaded model in memory
_model = None

def get_model():
    """Lazily load the SentenceTransformer model to avoid blocking app startup unnecessarily."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Note: Initial execution will download ~90MB of model weights.
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            raise ImportError("Please install sentence-transformers to use the ML pipeline.")
        except Exception as e:
            raise RuntimeError(f"Failed to load the pretrained model: {e}")
    return _model

def get_embedding(text: str) -> np.ndarray:
    """
    Generates a numerical vector embedding for the given text.
    The output is a numpy array of dimension 384 for all-MiniLM-L6-v2.
    """
    if not text or not text.strip():
        raise ValueError("Cannot generate an embedding for empty text.")
    model = get_model()
    # The model returns a numpy array representing the semantic meaning
    return model.encode(text)
