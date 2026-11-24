"""
This service orchestrates the semantic analysis by connecting the embeddings logic
with the similarity mathematics. It abstracts the ML operations from the API routers.
"""
import numpy as np
from typing import Dict, Any
from ml.embeddings.encoder import get_embedding
from ml.profiles.job_roles import get_role_profile

def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Computes the mathematical cosine similarity between two numeric vectors.
    Cosine similarity measures the angle between vectors, yielding a score between
    -1.0 and 1.0 (though practically 0.0 to 1.0 for these embeddings), where higher
    means more semantically similar.
    """
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    similarity = dot_product / (norm_a * norm_b)
    return float(similarity)

def analyze_resume_against_role(resume_text: str, target_role: str) -> Dict[str, Any]:
    """
    Executes the NLP pipeline comparing a resume against a target job role.
    Returns the computed semantic similarity and the dimension of the embedding space.
    """
    # 1. Fetch the natural language description of the target role
    role_description = get_role_profile(target_role)
    
    # 2. Generate embeddings for both texts using the Sentence Transformer
    resume_embedding = get_embedding(resume_text)
    role_embedding = get_embedding(role_description)
    
    # 3. Compute cosine similarity
    similarity_score = compute_cosine_similarity(resume_embedding, role_embedding)
    
    return {
        "target_job_role": target_role,
        "semantic_similarity": round(similarity_score, 4),
        "embedding_dimension": len(resume_embedding)
    }
