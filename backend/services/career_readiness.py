"""
Career Readiness Analyzer Service Layer for HireMind Milestone 9.

This service calculates a deterministic, explainable, and reproducible Career Readiness
Report from real stored HireMind data (interview responses, questions, and resume).

Key Principles:
1. No arbitrary or hallucinated AI scores.
2. Reuse existing all-MiniLM-L6-v2 embedding model via `ml.embeddings.encoder.get_model()`
   for the Resume Skill Match dimension.
3. Strict validation: requires completed interview, usable resume text, supported job role,
   and at least one response for each core question category (Technical, Problem Solving, Behavioral).
4. Deterministic aggregation formula:
   Overall = (Technical * 0.25) + (Problem Solving * 0.20) + (Communication * 0.20)
           + (Behavioral * 0.15) + (Resume Skill Match * 0.10) + (Interview Performance * 0.10)
5. Structured recommendation tiers:
   - Below 50: Needs substantial improvement
   - 50–69: Developing
   - 70–84: Solid
   - 85–100: Strong
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.readiness import CareerReadinessReport
from models.interview import InterviewResponse, InterviewSession, InterviewQuestion
from models.resume import Resume
from ml.embeddings.encoder import get_model
from ml.profiles.job_roles import get_role_profile
from ml.services.semantic_analysis import analyze_resume_against_role


def _compute_component(scores: List[float]) -> float:
    """
    Helper to compute the mathematical average for a list of scores.
    Raises ValueError if the input list is empty.
    """
    count = len(scores)
    if count == 0:
        raise ValueError("Cannot compute score for an empty list of values.")
    return sum(scores) / count


def calculate_technical_score(responses: List[Dict]) -> float:
    """
    Technical Knowledge - 25% of overall score.
    Calculates the average performance_score of 'Technical' responses.
    
    Args:
        responses: List of response dicts with 'category' and 'performance_score'.
        
    Returns:
        Average performance score for Technical questions (0.0 - 100.0).
    """
    scores = [
        r['performance_score']
        for r in responses
        if r.get('category') == 'Technical' and r.get('performance_score') is not None
    ]
    return _compute_component(scores)


def calculate_problem_solving_score(responses: List[Dict]) -> float:
    """
    Problem Solving - 20% of overall score.
    Calculates the average performance_score of 'Problem Solving' responses.
    
    Args:
        responses: List of response dicts with 'category' and 'performance_score'.
        
    Returns:
        Average performance score for Problem Solving questions (0.0 - 100.0).
    """
    scores = [
        r['performance_score']
        for r in responses
        if r.get('category') == 'Problem Solving' and r.get('performance_score') is not None
    ]
    return _compute_component(scores)


def calculate_behavioral_score(responses: List[Dict]) -> float:
    """
    Behavioral Readiness - 15% of overall score.
    Calculates the average performance_score of 'Behavioral' responses.
    
    Args:
        responses: List of response dicts with 'category' and 'performance_score'.
        
    Returns:
        Average performance score for Behavioral questions (0.0 - 100.0).
    """
    scores = [
        r['performance_score']
        for r in responses
        if r.get('category') == 'Behavioral' and r.get('performance_score') is not None
    ]
    return _compute_component(scores)


def calculate_communication_score(responses: List[Dict]) -> float:
    """
    Communication / Answer Quality - 20% of overall score.
    Calculates: 60% average semantic_similarity + 40% average completeness_score.
    
    Semantic similarity measures answer relevance and conceptual clarity, while
    completeness measures structural thoroughness, correlating directly with
    effective professional communication.
    
    Args:
        responses: List of response dicts containing 'semantic_similarity' and 'completeness_score'.
        
    Returns:
        Weighted communication score (0.0 - 100.0).
    """
    sim_scores = [
        r['semantic_similarity']
        for r in responses
        if r.get('semantic_similarity') is not None
    ]
    comp_scores = [
        r['completeness_score']
        for r in responses
        if r.get('completeness_score') is not None
    ]
    
    if not sim_scores or not comp_scores:
        raise ValueError("Cannot calculate communication score with missing responses.")
        
    avg_sim = _compute_component(sim_scores)
    avg_comp = _compute_component(comp_scores)
    return (0.60 * avg_sim) + (0.40 * avg_comp)


def calculate_interview_performance(responses: List[Dict]) -> float:
    """
    Interview Performance - 10% of overall score.
    Calculates the average performance_score across ALL questions in the session.
    
    Args:
        responses: List of response dicts with 'performance_score'.
        
    Returns:
        Average performance score across all session responses (0.0 - 100.0).
    """
    scores = [
        r['performance_score']
        for r in responses
        if r.get('performance_score') is not None
    ]
    return _compute_component(scores)


def calculate_resume_match(resume_text: str, target_role: str) -> float:
    """
    Resume / Skill Match - 10% of overall score.
    
    Reuses the existing cached SentenceTransformer model via `ml.embeddings.encoder.get_model()`
    and `analyze_resume_against_role` to compute cosine similarity between the resume text
    and the natural language target role profile.
    
    The cosine similarity is clamped to [0.0, 1.0] and scaled to [0.0, 100.0].
    
    Args:
        resume_text: Extracted plain text from the candidate's resume.
        target_role: Target job role title (e.g., 'Software Engineer').
        
    Returns:
        Resume skill match score (0.0 - 100.0).
    """
    # Verifies the model is available via cached get_model()
    _ = get_model()
    # Explicitly validate role profile exists
    get_role_profile(target_role)
    
    result = analyze_resume_against_role(resume_text, target_role)
    raw_sim = result.get('semantic_similarity', 0.0)
    # Cosine similarity is clamped to [0.0, 1.0] and converted to a 0-100 scale
    score = max(0.0, min(1.0, float(raw_sim))) * 100.0
    return round(score, 2)


def calculate_overall_readiness(
    tech: float,
    ps: float,
    comm: float,
    behav: float,
    resume: float,
    perf: float
) -> float:
    """
    Calculates the final deterministic overall Career Readiness score using mandated weights:
    - 25% Technical Knowledge
    - 20% Problem Solving
    - 20% Communication / Answer Quality
    - 15% Behavioral Readiness
    - 10% Resume / Skill Match
    - 10% Interview Performance
    
    Returns:
        Rounded overall readiness score (0.0 - 100.0).
    """
    score = (
        (tech * 0.25)
        + (ps * 0.20)
        + (comm * 0.20)
        + (behav * 0.15)
        + (resume * 0.10)
        + (perf * 0.10)
    )
    return round(score, 2)


def generate_recommendations(
    tech_score: float,
    ps_score: float,
    comm_score: float,
    behav_score: float,
    resume_score: float,
    perf_score: float
) -> List[str]:
    """
    Generates deterministic, actionable recommendations based on four readiness thresholds:
    - Below 50: Needs substantial improvement
    - 50–69: Developing
    - 70–84: Solid
    - 85–100: Strong
    
    Returns:
        List of recommendation strings for areas needing improvement or overall readiness.
    """
    recs: List[str] = []
    
    # 1. Technical Knowledge
    if tech_score < 50:
        recs.append("Focus on strengthening core technical concepts through targeted practice. (Needs substantial improvement)")
    elif tech_score < 70:
        recs.append("Deepen your technical knowledge in domain-specific problem areas. (Developing)")
        
    # 2. Problem Solving
    if ps_score < 50:
        recs.append("Practice structured problem-solving approaches and more challenging scenarios. (Needs substantial improvement)")
    elif ps_score < 70:
        recs.append("Work on edge-case handling and optimal solution design during problem-solving. (Developing)")
        
    # 3. Communication
    if comm_score < 50:
        recs.append("Work on explaining ideas clearly and providing complete, well-structured answers. (Needs substantial improvement)")
    elif comm_score < 70:
        recs.append("Practice concise articulation and thoroughly addressing all parts of interview prompts. (Developing)")
        
    # 4. Behavioral Readiness
    if behav_score < 50:
        recs.append("Practice structured behavioral responses using the STAR method with concrete outcomes. (Needs substantial improvement)")
    elif behav_score < 70:
        recs.append("Highlight specific leadership, collaboration, and conflict-resolution examples. (Developing)")
        
    # 5. Resume / Skill Match
    if resume_score < 50:
        recs.append("Strengthen skills and resume content that are most relevant to the selected target role. (Needs substantial improvement)")
    elif resume_score < 70:
        recs.append("Align resume project descriptions and keyword terminology more closely with role requirements. (Developing)")
        
    # 6. Interview Performance
    if perf_score < 50:
        recs.append("Review your interview responses and focus on improving consistency across questions. (Needs substantial improvement)")
    elif perf_score < 70:
        recs.append("Aim for higher consistency in answer depth across all interview categories. (Developing)")
        
    if not recs:
        min_score = min(tech_score, ps_score, comm_score, behav_score, resume_score, perf_score)
        if min_score >= 85:
            recs.append("You are showing strong readiness across measured dimensions. Keep up the good work! (Strong)")
        else:
            recs.append("You are showing solid readiness across measured dimensions with consistent performance. (Solid)")
        
    return recs


def get_component_recommendations(
    tech_score: float,
    ps_score: float,
    comm_score: float,
    behav_score: float,
    resume_score: float,
    perf_score: float
) -> Dict[str, str]:
    """
    Generates a dictionary of deterministic recommendations mapped by component,
    strictly aligned with the four readiness thresholds:
    - Below 50: Needs substantial improvement
    - 50–69: Developing
    - 70–84: Solid
    - 85–100: Strong
    
    Returns:
        Dictionary mapping component key to actionable recommendation string.
    """
    return {
        "technical": (
            "Focus on strengthening core technical concepts through targeted practice. (Needs substantial improvement)"
            if tech_score < 50
            else "Deepen your technical knowledge in domain-specific problem areas. (Developing)"
            if tech_score < 70
            else "Solid technical foundation demonstrated; continue refining advanced topics. (Solid)"
            if tech_score < 85
            else "Strong technical expertise and deep domain comprehension demonstrated. (Strong)"
        ),
        "problem_solving": (
            "Practice structured problem-solving approaches and more challenging scenarios. (Needs substantial improvement)"
            if ps_score < 50
            else "Work on edge-case handling and optimal solution design during problem-solving. (Developing)"
            if ps_score < 70
            else "Solid problem-solving methodology shown; focus on complex edge cases. (Solid)"
            if ps_score < 85
            else "Strong analytical reasoning and structured problem-solving demonstrated. (Strong)"
        ),
        "communication": (
            "Work on explaining ideas clearly and providing complete, well-structured answers. (Needs substantial improvement)"
            if comm_score < 50
            else "Practice concise articulation and thoroughly addressing all parts of interview prompts. (Developing)"
            if comm_score < 70
            else "Clear and articulate communication demonstrated with good structure. (Solid)"
            if comm_score < 85
            else "Strong communication skills; highly articulate, structured, and thorough. (Strong)"
        ),
        "behavioral": (
            "Practice structured behavioral responses using the STAR method with concrete outcomes. (Needs substantial improvement)"
            if behav_score < 50
            else "Highlight specific leadership, collaboration, and conflict-resolution examples. (Developing)"
            if behav_score < 70
            else "Solid behavioral readiness demonstrated with clear personal contributions. (Solid)"
            if behav_score < 85
            else "Strong leadership presence, situational judgment, and behavioral readiness shown. (Strong)"
        ),
        "resume_skill_match": (
            "Strengthen skills and resume content that are most relevant to the selected target role. (Needs substantial improvement)"
            if resume_score < 50
            else "Align resume project descriptions and keyword terminology more closely with role requirements. (Developing)"
            if resume_score < 70
            else "Solid alignment between resume background and target role expectations. (Solid)"
            if resume_score < 85
            else "Strong skill match; resume profile closely aligns with target role expectations. (Strong)"
        ),
        "interview_performance": (
            "Review your interview responses and focus on improving consistency across questions. (Needs substantial improvement)"
            if perf_score < 50
            else "Aim for higher consistency in answer depth across all interview categories. (Developing)"
            if perf_score < 70
            else "Solid overall interview performance with steady responses across categories. (Solid)"
            if perf_score < 85
            else "Strong overall interview performance with consistently high answer quality. (Strong)"
        )
    }


def generate_report(
    db: Session,
    user_id: int,
    session_id: int,
    resume_id: int
) -> CareerReadinessReport:
    """
    Main Career Readiness analysis entrypoint.
    
    Performs complete validation:
    1. Verifies interview session exists, belongs to user, and is COMPLETED.
    2. Verifies resume exists, belongs to user, and has usable text.
    3. Fetches InterviewResponses joined with InterviewQuestions.
    4. Validates that EVERY response has all required evaluation fields:
       - performance_score
       - semantic_similarity
       - concept_coverage
       - completeness_score
    5. Enforces at least one response for Technical, Problem Solving, and Behavioral.
    6. Explicitly validates target_job_role against supported role profiles.
    7. Calculates all component scores and overall readiness.
    8. Persists the CareerReadinessReport to the database with rollback on failure.
    
    Args:
        db: SQLAlchemy database session.
        user_id: Authenticated user ID.
        session_id: Target InterviewSession ID.
        resume_id: Target Resume ID.
        
    Returns:
        Persisted CareerReadinessReport record.
        
    Raises:
        ValueError: For missing records, unauthorized access, incomplete sessions, unsupported roles,
                    missing evaluation fields, or missing required categories.
        RuntimeError: For database persistence errors.
    """
    # 1. Fetch & Verify Session
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise ValueError("Interview session not found.")
    if session.user_id != user_id:
        raise ValueError("Not authorized to access this interview session.")
    if session.status != "COMPLETED":
        raise ValueError("Cannot generate readiness report for an incomplete interview.")
        
    # 2. Fetch & Verify Resume
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise ValueError("Resume not found.")
    if resume.user_id != user_id:
        raise ValueError("Not authorized to access this resume.")
    if not resume.extracted_text or not resume.extracted_text.strip():
        raise ValueError("Resume text is missing or unreadable.")
        
    # 3. Explicitly validate target_job_role using existing job role profile infrastructure
    target_role = session.target_job_role
    try:
        get_role_profile(target_role)
    except ValueError as e:
        raise ValueError(f"Invalid target job role: {str(e)}")

    # 4. Fetch Responses joined with Questions
    stmt = (
        select(InterviewResponse, InterviewQuestion)
        .join(InterviewQuestion, InterviewResponse.question_id == InterviewQuestion.id)
        .where(InterviewResponse.session_id == session_id)
    )
    rows = db.execute(stmt).all()
    if not rows:
        raise ValueError("No interview responses found for this session.")
        
    responses = []
    has_tech = False
    has_ps = False
    has_behav = False
    
    # Validate EVERY response has ALL required evaluation fields before computing any component
    for resp, q in rows:
        if (
            resp.performance_score is None
            or resp.semantic_similarity is None
            or resp.concept_coverage is None
            or resp.completeness_score is None
        ):
            raise ValueError("Required AI evaluation data is missing from one or more responses.")
            
        category = q.category
        if category == 'Technical':
            has_tech = True
        elif category == 'Problem Solving':
            has_ps = True
        elif category == 'Behavioral':
            has_behav = True
            
        responses.append({
            "category": category,
            "performance_score": resp.performance_score,
            "semantic_similarity": resp.semantic_similarity,
            "concept_coverage": resp.concept_coverage,
            "completeness_score": resp.completeness_score
        })
        
    # Enforce minimum category requirements (never substitute missing data with 0)
    if not has_tech:
        raise ValueError("Missing Technical responses. Cannot calculate report.")
    if not has_ps:
        raise ValueError("Missing Problem Solving responses. Cannot calculate report.")
    if not has_behav:
        raise ValueError("Missing Behavioral responses. Cannot calculate report.")
        
    # 5. Calculate Scores
    try:
        resume_score = calculate_resume_match(resume.extracted_text, target_role)
    except Exception as e:
        raise ValueError(f"Failed to analyze resume match: {str(e)}")
        
    tech_score = calculate_technical_score(responses)
    ps_score = calculate_problem_solving_score(responses)
    behav_score = calculate_behavioral_score(responses)
    comm_score = calculate_communication_score(responses)
    perf_score = calculate_interview_performance(responses)
    
    # Defensive clamp to [0.0, 100.0] and round to 2 decimal places
    tech_score = max(0.0, min(100.0, round(tech_score, 2)))
    ps_score = max(0.0, min(100.0, round(ps_score, 2)))
    behav_score = max(0.0, min(100.0, round(behav_score, 2)))
    comm_score = max(0.0, min(100.0, round(comm_score, 2)))
    perf_score = max(0.0, min(100.0, round(perf_score, 2)))
    resume_score = max(0.0, min(100.0, round(resume_score, 2)))
    
    overall = calculate_overall_readiness(
        tech_score, ps_score, comm_score, behav_score, resume_score, perf_score
    )
    
    # 6. Persist the CareerReadinessReport
    report = CareerReadinessReport(
        user_id=user_id,
        interview_session_id=session_id,
        resume_id=resume_id,
        target_job_role=target_role,
        technical_score=tech_score,
        problem_solving_score=ps_score,
        communication_score=comm_score,
        behavioral_score=behav_score,
        resume_skill_match_score=resume_score,
        interview_performance_score=perf_score,
        overall_readiness_score=overall
    )
    
    try:
        db.add(report)
        db.commit()
        db.refresh(report)
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Database persistence failed: {str(e)}")
        
    return report
