# scripts/test_generation.py
from pipeline import LocalQuestionPipeline
import json

def test_pipeline():
    """Test the complete pipeline"""
    
    pipeline = LocalQuestionPipeline()
    
    # Test generation
    questions = pipeline.generate_questions(
        topic="Mechanics",
        num_questions=2,
        difficulty="medium"
    )
    
    print(f"Generated {len(questions)} questions")
    print(json.dumps([q.model_dump() for q in questions], indent=2))

if __name__ == "__main__":
    test_pipeline()