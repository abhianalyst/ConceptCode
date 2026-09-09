# apps/practice/adaptive.py

from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.core.models import Question


class AdaptiveDifficulty:
    """
    ML-based adaptive difficulty system.
    Selects the next question difficulty based on student performance.
    """
    
    DIFFICULTY_LEVELS = ['Easy', 'Medium', 'Hard']
    
    def __init__(self, user, topic):
        self.user = user
        self.topic = topic
        self.performance = self._get_performance_data()
        self.current_level = self._get_current_level()
    
    def _get_performance_data(self):
        """Get student's performance data for this topic"""
        from .models import PracticeAttempt
        
        # Get attempts from the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        attempts = PracticeAttempt.objects.filter(
            session__user=self.user,
            session__topic=self.topic,
            answered_at__gte=thirty_days_ago
        )
        
        performance = {}
        for level in self.DIFFICULTY_LEVELS:
            level_attempts = attempts.filter(question__difficulty=level)
            total = level_attempts.count()
            correct = level_attempts.filter(is_correct=True).count()
            accuracy = round((correct / total) * 100, 1) if total > 0 else 0
            
            performance[level] = {
                'total': total,
                'correct': correct,
                'accuracy': accuracy,
                'attempts': level_attempts
            }
        
        return performance
    
    def _get_current_level(self):
        """Determine current difficulty level based on performance"""
        # Start with Easy if no data
        if all(p['total'] == 0 for p in self.performance.values()):
            return 'Easy'
        
        # Find the level with most attempts
        max_attempts = 0
        current_level = 'Easy'
        for level, data in self.performance.items():
            if data['total'] > max_attempts:
                max_attempts = data['total']
                current_level = level
        
        return current_level
    
    def get_next_difficulty(self):
        """
        Determine the next difficulty level based on performance.
        
        Returns:
            str: 'Easy', 'Medium', or 'Hard'
        """
        easy = self.performance.get('Easy', {})
        medium = self.performance.get('Medium', {})
        hard = self.performance.get('Hard', {})
        
        # If no data, start with Easy
        if easy['total'] == 0 and medium['total'] == 0 and hard['total'] == 0:
            return 'Easy'
        
        # Rule 1: If doing well on Easy, move to Medium
        if easy['total'] >= 5 and easy['accuracy'] >= 70:
            if medium['total'] < 5 or medium['accuracy'] >= 50:
                return 'Medium'
        
        # Rule 2: If doing well on Medium, move to Hard
        if medium['total'] >= 5 and medium['accuracy'] >= 70:
            if hard['total'] < 5 or hard['accuracy'] >= 40:
                return 'Hard'
        
        # Rule 3: If struggling on Hard, move down
        if hard['total'] >= 3 and hard['accuracy'] < 40:
            return 'Medium'
        
        # Rule 4: If struggling on Medium, move down
        if medium['total'] >= 3 and medium['accuracy'] < 40:
            return 'Easy'
        
        # Default: stay at current level
        return self.current_level
    
    def get_performance_summary(self):
        """Get a summary of performance data"""
        summary = []
        for level, data in self.performance.items():
            summary.append({
                'level': level,
                'accuracy': data['accuracy'],
                'attempts': data['total'],
                'correct': data['correct']
            })
        return summary
    
    def should_use_adaptive(self):
        """Check if enough data exists for adaptive mode"""
        total_attempts = sum(p['total'] for p in self.performance.values())
        return total_attempts >= 3


# ============================================================
# ADAPTIVE DIFFICULTY SERVICE
# ============================================================

class AdaptiveService:
    """Service class for adaptive difficulty selection"""
    
    @staticmethod
    def get_adaptive_question(session, difficulty=None):
        """
        Get the next question with adaptive difficulty.
        If difficulty is specified, use that.
        Otherwise, use the adaptive algorithm.
        """
        from .services import get_next_question
        
        if difficulty:
            return get_next_question(session=session, difficulty=difficulty)
        
        # Use adaptive logic
        adaptive = AdaptiveDifficulty(session.user, session.topic)
        next_difficulty = adaptive.get_next_difficulty()
        
        # Try to get a question with the recommended difficulty
        question = get_next_question(session=session, difficulty=next_difficulty)
        
        # If no question available at that difficulty, fallback to any difficulty
        if question is None:
            question = get_next_question(session=session)
        
        return question, next_difficulty
    
    @staticmethod
    def get_next_adaptive_question(session):
        """Get next question with adaptive difficulty"""
        return AdaptiveService.get_adaptive_question(session)