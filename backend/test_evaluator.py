from services.answer_evaluator import evaluate_answer

def test_evaluator_bounds():
    # Test completely matching answer
    result_high = evaluate_answer(
        candidate_text="The quick brown fox jumps over the lazy dog.",
        expected_answer="The quick brown fox jumps over the lazy dog.",
        key_concepts=["quick", "brown", "fox", "jumps", "lazy", "dog"],
        rubric_criteria=["Mentions fox", "Mentions dog"]
    )
    assert 85 <= result_high["overall_score"] <= 100
    assert result_high["semantic_similarity"] > 95
    assert result_high["concept_coverage"] == 100
    
    # Test completely unrelated answer
    result_low = evaluate_answer(
        candidate_text="I prefer eating pizza and pasta on Fridays.",
        expected_answer="The quick brown fox jumps over the lazy dog.",
        key_concepts=["quick", "brown", "fox", "jumps", "lazy", "dog"],
        rubric_criteria=["Mentions fox", "Mentions dog"]
    )
    assert 0 <= result_low["overall_score"] <= 30
    
    # Test empty or missing metadata gracefully defaults
    result_graceful = evaluate_answer(
        candidate_text="This is an answer.",
        expected_answer="This is an answer.",
        key_concepts=[],
        rubric_criteria=[]
    )
    assert result_graceful["concept_coverage"] == 100
    assert result_graceful["completeness_score"] == 100
    assert result_graceful["overall_score"] >= 95
    
    # Determinism check
    result_high_2 = evaluate_answer(
        candidate_text="The quick brown fox jumps over the lazy dog.",
        expected_answer="The quick brown fox jumps over the lazy dog.",
        key_concepts=["quick", "brown", "fox", "jumps", "lazy", "dog"],
        rubric_criteria=["Mentions fox", "Mentions dog"]
    )
    assert result_high["overall_score"] == result_high_2["overall_score"]
    
    print("All Evaluator tests passed!")

if __name__ == "__main__":
    test_evaluator_bounds()
