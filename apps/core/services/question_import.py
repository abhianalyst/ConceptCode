# apps/core/services/question_import.py
"""
Question import service for JSON/CSV imports.
"""

import csv
import json
import hashlib
from io import StringIO
from typing import Dict, List, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from transformers import data
from apps.core.models import Subject, Chapter, Topic, Question, QuestionDifficulty
import random


class QuestionImportService:
    """Service for importing questions from JSON and CSV."""
    
    def __init__(self, create_missing=True, skip_duplicates=True):
        self.create_missing = create_missing
        self.skip_duplicates = skip_duplicates
        self.stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': []
        }
    
    def import_from_json(self, json_data: str) -> Dict:
        """Import questions from JSON string."""
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            self.stats['errors'].append(f"Invalid JSON: {str(e)}")
            return self.stats
        
        if isinstance(data, dict):
            questions = [data]
        elif isinstance(data, list):
            questions = data
        else:
            self.stats['errors'].append("JSON must be an object or array")
            return self.stats
        
        with transaction.atomic():
            for idx, question_data in enumerate(questions):
                try:
                    self._import_single_question(question_data)
                except Exception as e:
                    self.stats['errors'].append(f"Question {idx + 1}: {str(e)}")
        
        return self.stats
    
    def import_from_csv(self, csv_data: str) -> Dict:
        """Import questions from CSV string."""
        try:
            csv_file = StringIO(csv_data)
            reader = csv.DictReader(csv_file)
            
            with transaction.atomic():
                for idx, row in enumerate(reader):
                    try:
                        question_data = self._csv_row_to_canonical(row)
                        self._import_single_question(question_data)
                    except Exception as e:
                        self.stats['errors'].append(f"Row {idx + 2}: {str(e)}")
                        
        except Exception as e:
            self.stats['errors'].append(f"CSV parsing error: {str(e)}")
        
        return self.stats
    
    def _import_single_question(self, data: Dict):
        """Import a single question with randomized option order."""

        # ============================================================
        # 1. Resolve topic
        # ============================================================
        topic = self._resolve_topic(
            data.get('subject', ''),
            data.get('chapter', ''),
            data.get('topic', '')
        )

        # ============================================================
        # 2. Generate fingerprint
        # ============================================================
        fingerprint = self._generate_fingerprint(data)

        # ============================================================
        # 3. Check duplicates
        # ============================================================
        if self.skip_duplicates and Question.objects.filter(
            question_fingerprint=fingerprint
        ).exists():
            self.stats['skipped'] += 1
            return

        # ============================================================
        # 4. Get options
        # ============================================================
        options = data.get('options', {})

        # Convert list format:
        # ["Option 1", "Option 2", "Option 3", "Option 4"]
        # into:
        # {"A": "...", "B": "...", "C": "...", "D": "..."}
        if isinstance(options, list):
            options = {
                'A': options[0] if len(options) > 0 else '',
                'B': options[1] if len(options) > 1 else '',
                'C': options[2] if len(options) > 2 else '',
                'D': options[3] if len(options) > 3 else '',
            }

        elif not isinstance(options, dict):
            options = {
                'A': '',
                'B': '',
                'C': '',
                'D': '',
            }

        # ============================================================
        # 5. Extract option texts
        # ============================================================
        option_labels = ['A', 'B', 'C', 'D']

        option_texts = [
            options.get('A', ''),
            options.get('B', ''),
            options.get('C', ''),
            options.get('D', ''),
        ]

        # ============================================================
        # 6. Determine original correct answer
        # ============================================================
        correct_original = str(
            data.get('correct_answer', 'A')
        ).strip().upper()

        # Handle invalid correct answer safely
        if correct_original not in option_labels:
            correct_original = 'A'

        correct_index = option_labels.index(correct_original)

        # ============================================================
        # 7. Shuffle options
        # ============================================================
        shuffled_indices = list(range(4))
        random.shuffle(shuffled_indices)

        shuffled_options = {
            'A': option_texts[shuffled_indices[0]],
            'B': option_texts[shuffled_indices[1]],
            'C': option_texts[shuffled_indices[2]],
            'D': option_texts[shuffled_indices[3]],
        }

        # ============================================================
        # 8. Find new correct answer
        # ============================================================
        new_correct = option_labels[
            shuffled_indices.index(correct_index)
        ]

        # ============================================================
        # 9. Prepare question data
        # ============================================================
        question_data = {
            'topic': topic,

            'question': data.get('question', '').strip(),

            'question_fingerprint': fingerprint,

            'option_a': shuffled_options['A'],
            'option_b': shuffled_options['B'],
            'option_c': shuffled_options['C'],
            'option_d': shuffled_options['D'],

            'correct_answer': new_correct,

            'explanation': data.get('explanation', ''),

            'difficulty': self._normalize_difficulty(
                data.get('difficulty', 'Easy')
            ),

            'source': data.get('source', ''),

            'year_tag': data.get('year_tag', ''),

            'is_active': data.get('is_active', True),
        }

        # ============================================================
        # 10. Create question
        # ============================================================
        question, created = Question.objects.get_or_create(
            question_fingerprint=fingerprint,
            defaults=question_data
        )

        # ============================================================
        # 11. Update statistics
        # ============================================================
        if created:
            self.stats['created'] += 1
        else:
            self.stats['updated'] += 1


    def _resolve_topic(self, subject_name: str, chapter_name: str, topic_name: str) -> Topic:
        """Resolve or create subject, chapter, topic."""
        subject, _ = Subject.objects.get_or_create(
            name=subject_name.strip(),
            defaults={'is_active': True}
        )
        
        chapter, _ = Chapter.objects.get_or_create(
            subject=subject,
            name=chapter_name.strip(),
            defaults={'is_active': True}
        )
        
        topic, _ = Topic.objects.get_or_create(
            chapter=chapter,
            name=topic_name.strip(),
            defaults={'is_active': True}
        )
        
        return topic
    
    def _generate_fingerprint(self, data: Dict) -> str:
        """Generate unique fingerprint for question."""
        options = data.get('options', {})
        if isinstance(options, list):
            options = {
                'A': options[0] if len(options) > 0 else '',
                'B': options[1] if len(options) > 1 else '',
                'C': options[2] if len(options) > 2 else '',
                'D': options[3] if len(options) > 3 else '',
            }
        
        fingerprint_data = {
            'question': data.get('question', '').strip(),
            'options': [
                options.get('A', ''),
                options.get('B', ''),
                options.get('C', ''),
                options.get('D', ''),
            ],
            'correct_answer': data.get('correct_answer', '').strip().upper(),
        }
        
        text = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(text.encode()).hexdigest()
    
    def _normalize_difficulty(self, difficulty: str) -> str:
        """Normalize difficulty value."""
        difficulty_map = {
            'easy': 'Easy',
            'medium': 'Medium',
            'hard': 'Hard',
            'EASY': 'Easy',
            'MEDIUM': 'Medium',
            'HARD': 'Hard',
        }
        return difficulty_map.get(str(difficulty).lower(), 'Easy')
    
    def _csv_row_to_canonical(self, row: Dict) -> Dict:
        """Convert CSV row to canonical format."""
        return {
            'subject': row.get('subject', '').strip(),
            'chapter': row.get('chapter', '').strip(),
            'topic': row.get('topic', '').strip(),
            'question': row.get('question', '').strip(),
            'options': {
                'A': row.get('option_a', '').strip(),
                'B': row.get('option_b', '').strip(),
                'C': row.get('option_c', '').strip(),
                'D': row.get('option_d', '').strip(),
            },
            'correct_answer': row.get('correct_answer', '').strip().upper(),
            'explanation': row.get('explanation', '').strip(),
            'difficulty': row.get('difficulty', 'Easy').strip(),
            'source': row.get('source', '').strip(),
            'year_tag': row.get('year_tag', '').strip(),
        }