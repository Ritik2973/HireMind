from sentence_transformers import util
from typing import Dict, List, Any

from ml.embeddings.encoder import get_model

# Empirical heuristic threshold for determining if a concept is covered.
# This is a tunable parameter, not a universal scientific threshold.
CONCEPT_SIMILARITY_THRESHOLD = 0.40


def generate_feedback(sim: float, cov: float, comp: float, overall: float) -> str:
    """
    Generates deterministic, actionable feedback based on component scores.
    """
    if overall >= 85:
        feedback = "Excellent answer! You demonstrated a very strong understanding of the key concepts."
    elif overall >= 70:
        feedback = "Good answer. You hit several important points, but there is some room for more depth."
    elif overall >= 50:
        feedback = "Fair attempt, but you missed some critical concepts or details."
    else:
        feedback = "Your answer was either off-topic or lacked the fundamental concepts expected."

    strengths = []
    if cov >= 70:
        strengths.append("You covered the required key concepts well.")
    elif comp >= 70:
        strengths.append("You addressed the multiple aspects of the rubric comprehensively.")
        
    improvements = []
    if cov < 50:
        improvements.append("Ensure you touch on all the specific terminology and key concepts.")
    if comp < 50:
        improvements.append("Try to expand on your points to cover all the aspects asked in the question.")
        
    if strengths:
        feedback += f" Strengths: {' '.join(strengths)}"
    if improvements:
        feedback += f" Areas to improve: {' '.join(improvements)}"
        
    return feedback


def evaluate_answer(
    candidate_text: str, 
    expected_answer: str, 
    key_concepts: List[str], 
    rubric_criteria: List[str]
) -> Dict[str, Any]:
    """
    Evaluates a candidate's answer against the expected answer, key concepts, and rubric criteria.
    Uses pretrained Transformer embeddings (all-MiniLM-L6-v2) for semantic evaluation.
    
    Returns a dictionary with:
    - semantic_similarity (0-100)
    - concept_coverage (0-100)
    - completeness_score (0-100)
    - overall_score (0-100)
    - feedback (str)
    """
    if not candidate_text or not candidate_text.strip():
        raise ValueError("Candidate answer cannot be empty.")
        
    if not expected_answer or not expected_answer.strip():
        raise ValueError("Expected answer cannot be empty.")

    if not key_concepts:
        raise ValueError("Question must contain key concepts.")

    if not rubric_criteria:
        raise ValueError("Question must contain rubric criteria.")

    model = get_model()
    
    # Precompute candidate embedding
    candidate_emb = model.encode(candidate_text, convert_to_tensor=True)
    expected_emb = model.encode(expected_answer, convert_to_tensor=True)
    
    # 1. Semantic Similarity Score (35%)
    # Note: negative cosine similarity is treated as 0
    # positive similarity in [0, 1] is mapped to [0, 100]
    raw_sim = util.cos_sim(candidate_emb, expected_emb).item()
    sim_score = max(0.0, raw_sim) * 100.0
    
    # 2. Key Concept Coverage Score (45%)
    concept_embs = model.encode(key_concepts, convert_to_tensor=True)
    # Compute similarities of candidate answer against all concepts at once
    concept_sims = util.cos_sim(candidate_emb, concept_embs)[0].cpu().numpy()
    
    covered = 0
    for i, concept in enumerate(key_concepts):
        # Threshold to consider a concept "covered"
        # We also do a fallback exact string match check for robustness
        if concept_sims[i] > CONCEPT_SIMILARITY_THRESHOLD or concept.lower() in candidate_text.lower():
            covered += 1
    
    cov_score = (covered / len(key_concepts)) * 100.0
        
    # 3. Completeness / Rubric Score (20%)
    # Evaluates how well the answer addresses all parts of the rubric criteria
    rubric_embs = model.encode(rubric_criteria, convert_to_tensor=True)
    rubric_sims = util.cos_sim(candidate_emb, rubric_embs)[0].cpu().numpy()
    
    total_segment_sim = 0.0
    for r_sim in rubric_sims:
        total_segment_sim += max(0.0, r_sim)
        
    comp_score = (total_segment_sim / len(rubric_criteria)) * 100.0
        
    # 4. Final Deterministic Score
    overall_score = (0.35 * sim_score) + (0.45 * cov_score) + (0.20 * comp_score)
    overall_score = max(0.0, min(100.0, overall_score))
    
    feedback = generate_feedback(sim_score, cov_score, comp_score, overall_score)
    
    return {
        "semantic_similarity": round(sim_score, 2),
        "concept_coverage": round(cov_score, 2),
        "completeness_score": round(comp_score, 2),
        "overall_score": round(overall_score, 2),
        "feedback": feedback
    }
