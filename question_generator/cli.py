# cli.py (Modified - Local Only)
import click
from pipeline import LocalQuestionPipeline
import json
from typing import Optional

@click.group()
def cli():
    """Local Question Generator CLI"""
    pass

@cli.command()
@click.option('--topic', required=True, help='Topic for questions')
@click.option('--num', default=5, help='Number of questions')
@click.option('--difficulty', default='medium', 
              type=click.Choice(['easy', 'medium', 'hard']))
@click.option('--question-type', multiple=True,
              type=click.Choice(['MCQ', 'ShortAnswer', 'LongAnswer', 'Numerical']))
@click.option('--output', help='Output file path')
@click.option('--subtopic', help='Specific subtopic')
def generate(topic, num, difficulty, question_type, output, subtopic):
    """Generate questions using local LLM"""
    
    # Initialize pipeline
    pipeline = LocalQuestionPipeline()
    
    # Generate questions
    print(f"Generating {num} questions about '{topic}'...")
    questions = pipeline.generate_questions(
        topic=topic,
        num_questions=num,
        difficulty=difficulty,
        question_types=list(question_type) if question_type else None,
        subtopic=subtopic
    )
    
    # Format output
    output_data = {
        'topic': topic,
        'subtopic': subtopic,
        'difficulty': difficulty,
        'questions': [
            {
                'question': q.question_text,
                'answer': q.answer_text,
                'options': q.options,
                'type': q.question_type.value,
                'difficulty': q.difficulty.value,
                'marks': q.marks,
                'explanation': q.explanation
            }
            for q in questions
        ]
    }
    
    # Output
    if output:
        with open(output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"✅ Saved to {output}")
    else:
        print(json.dumps(output_data, indent=2))

@cli.command()
@click.option('--textbook', required=True, help='Path to textbook JSON')
@click.option('--chunk-size', default=512, help='Chunk size for processing')
def setup_rag(textbook, chunk_size):
    """Setup RAG pipeline with textbook content"""
    
    pipeline = LocalQuestionPipeline()
    pipeline.setup_rag_pipeline(textbook_json_path=textbook)
    print("✅ RAG pipeline setup complete")

@cli.command()
def check_models():
    """Check available local models"""
    
    from local_llm.model_loader import LocalModelLoader
    loader = LocalModelLoader()
    models = loader.get_model_info()
    
    print("\nAvailable Models:")
    print("-" * 40)
    
    for model_type, model_list in models.items():
        print(f"\n{model_type.upper()}:")
        if model_list:
            for model in model_list:
                print(f"  ✓ {model}")
        else:
            print("  ✗ No models found")
    
    print("\nTo download models, run: python scripts/download_models.py")

if __name__ == "__main__":
    cli()