"""
Machine Learning service for weak area detection.

Uses:
- Decision Tree Classifier
- Random Forest Classifier
- Scikit-Learn for training
- Joblib for model serialization
"""

import os
import joblib
import numpy as np
import logging
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Q, Avg

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from apps.core.models import Topic, Question
from apps.practice.models import PracticeAttempt

logger = logging.getLogger(__name__)


# Model storage path
ML_MODELS_DIR = Path(__file__).parent / "ml_models"
ML_MODELS_DIR.mkdir(exist_ok=True)

DECISION_TREE_MODEL = ML_MODELS_DIR / "decision_tree.joblib"
RANDOM_FOREST_MODEL = ML_MODELS_DIR / "random_forest.joblib"


class FeatureExtractor:
    """Extract features from user practice data for ML model."""
    
    @staticmethod
    def extract_features(user, topic):
        """
        Extract features from a user's practice data for a specific topic.
        
        Returns:
            dict or None: Feature dictionary, or None if not enough data
        """
        # Get all attempts for this user on this topic
        attempts = PracticeAttempt.objects.filter(
            session__user=user,
            session__topic=topic
        ).select_related('question')
        
        total_attempts = attempts.count()
        
        if total_attempts == 0:
            return None
        
        # Basic features
        correct_attempts = attempts.filter(is_correct=True).count()
        accuracy = (correct_attempts / total_attempts) * 100
        
        avg_time = attempts.aggregate(
            avg=Avg('time_taken')
        )['avg'] or 0.0
        
        # Difficulty-wise accuracy
        easy_attempts = attempts.filter(question__difficulty='Easy')
        medium_attempts = attempts.filter(question__difficulty='Medium')
        hard_attempts = attempts.filter(question__difficulty='Hard')
        
        easy_accuracy = FeatureExtractor._safe_accuracy(easy_attempts)
        medium_accuracy = FeatureExtractor._safe_accuracy(medium_attempts)
        hard_accuracy = FeatureExtractor._safe_accuracy(hard_attempts)
        
        # Recent trend (last 7 days vs older)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_attempts = attempts.filter(answered_at__gte=seven_days_ago)
        recent_accuracy = FeatureExtractor._safe_accuracy(recent_attempts)
        
        return {
            'accuracy': round(accuracy, 2),
            'attempts': total_attempts,
            'avg_time': round(avg_time, 2),
            'easy_accuracy': round(easy_accuracy, 2),
            'medium_accuracy': round(medium_accuracy, 2),
            'hard_accuracy': round(hard_accuracy, 2),
            'recent_accuracy': round(recent_accuracy, 2),
        }
    
    @staticmethod
    def _safe_accuracy(attempts):
        """Calculate accuracy safely (avoid division by zero)."""
        total = attempts.count()
        if total == 0:
            return 0.0
        correct = attempts.filter(is_correct=True).count()
        return (correct / total) * 100
    
    @staticmethod
    def features_to_array(features):
        """Convert feature dict to numpy array for ML."""
        return np.array([[
            features['accuracy'],
            features['attempts'],
            features['avg_time'],
            features['easy_accuracy'],
            features['medium_accuracy'],
            features['hard_accuracy'],
            features['recent_accuracy'],
        ]])


class ModelTrainer:
    """Train ML models using synthetic + real data."""
    
    FEATURE_NAMES = [
        'accuracy', 'attempts', 'avg_time',
        'easy_accuracy', 'medium_accuracy',
        'hard_accuracy', 'recent_accuracy'
    ]
    
    @staticmethod
    def generate_training_data():
        """
        Generate training data using rules.
        
        In production, this would use actual labeled data.
        For the MVP, we generate synthetic data based on 
        rule-based classifications.
        
        Returns:
            tuple: (X, y) feature matrix and labels
        """
        np.random.seed(42)
        X = []
        y = []
        
        # Generate synthetic training samples
        for _ in range(2000):
            accuracy = np.random.uniform(0, 100)
            attempts = np.random.randint(1, 50)
            avg_time = np.random.uniform(10, 120)
            easy_accuracy = np.random.uniform(max(0, accuracy - 20), min(100, accuracy + 20))
            medium_accuracy = np.random.uniform(max(0, accuracy - 30), min(100, accuracy + 30))
            hard_accuracy = np.random.uniform(max(0, accuracy - 40), min(100, accuracy + 40))
            recent_accuracy = np.random.uniform(max(0, accuracy - 15), min(100, accuracy + 15))
            
            features = [
                accuracy, attempts, avg_time,
                easy_accuracy, medium_accuracy,
                hard_accuracy, recent_accuracy
            ]
            
            # Rule-based labeling
            label = ModelTrainer._rule_based_label(features)
            
            X.append(features)
            y.append(label)
        
        return np.array(X), np.array(y)
    
    @staticmethod
    def _rule_based_label(features):
        """
        Rule-based classification for training data.
        
        Returns:
            str: 'Strong', 'Moderate', or 'Weak'
        """
        accuracy = features[0]
        attempts = features[1]
        recent_accuracy = features[6]
        
        # Strong: high accuracy + enough attempts + no decline
        if accuracy >= 75 and attempts >= 10 and recent_accuracy >= 65:
            return 'Strong'
        
        # Weak: low accuracy or significant decline
        if accuracy < 50 or (attempts >= 5 and recent_accuracy < 40):
            return 'Weak'
        
        # Otherwise: Moderate
        return 'Moderate'
    
    @staticmethod
    def train_models():
        """
        Train both Decision Tree and Random Forest models.
        
        Returns:
            dict: Training results
        """
        logger.info("Starting model training...")
        
        # Generate training data
        X, y = ModelTrainer.generate_training_data()
        
        # Split into train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        results = {}
        
        # ============================================================
        # Train Decision Tree
        # ============================================================
        logger.info("Training Decision Tree...")
        dt_model = DecisionTreeClassifier(
            max_depth=5,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        )
        dt_model.fit(X_train, y_train)
        dt_predictions = dt_model.predict(X_test)
        dt_accuracy = accuracy_score(y_test, dt_predictions)
        
        # Save model
        joblib.dump(dt_model, DECISION_TREE_MODEL)
        
        results['decision_tree'] = {
            'accuracy': round(dt_accuracy * 100, 2),
            'report': classification_report(y_test, dt_predictions, zero_division=0),
            'model_path': str(DECISION_TREE_MODEL)
        }
        logger.info(f"Decision Tree trained: {dt_accuracy:.2%} accuracy")
        
        # ============================================================
        # Train Random Forest
        # ============================================================
        logger.info("Training Random Forest...")
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train, y_train)
        rf_predictions = rf_model.predict(X_test)
        rf_accuracy = accuracy_score(y_test, rf_predictions)
        
        # Save model
        joblib.dump(rf_model, RANDOM_FOREST_MODEL)
        
        results['random_forest'] = {
            'accuracy': round(rf_accuracy * 100, 2),
            'report': classification_report(y_test, rf_predictions, zero_division=0),
            'model_path': str(RANDOM_FOREST_MODEL),
            'feature_importance': dict(zip(
                ModelTrainer.FEATURE_NAMES,
                [round(x, 4) for x in rf_model.feature_importances_]
            ))
        }
        logger.info(f"Random Forest trained: {rf_accuracy:.2%} accuracy")
        
        return results


class PerformancePredictor:
    """Predict topic performance using trained ML model."""
    
    _model = None
    
    @classmethod
    def load_model(cls):
        """Load the trained model (cached)."""
        if cls._model is None:
            if RANDOM_FOREST_MODEL.exists():
                cls._model = joblib.load(RANDOM_FOREST_MODEL)
                logger.info("Loaded Random Forest model")
            elif DECISION_TREE_MODEL.exists():
                cls._model = joblib.load(DECISION_TREE_MODEL)
                logger.info("Loaded Decision Tree model (fallback)")
            else:
                logger.warning("No trained model found. Using rule-based fallback.")
        return cls._model
    
    @classmethod
    def predict(cls, user, topic):
        """
        Predict performance for a user on a topic.
        
        Returns:
            dict: {
                'classification': str,
                'confidence': float,
                'features': dict,
                'method': 'ml' or 'rule-based'
            }
        """
        features = FeatureExtractor.extract_features(user, topic)
        
        if features is None:
            return None
        
        model = cls.load_model()
        
        # Try ML prediction
        if model is not None:
            try:
                X = FeatureExtractor.features_to_array(features)
                classification = model.predict(X)[0]
                
                # Get confidence from probability
                probabilities = model.predict_proba(X)[0]
                confidence = float(max(probabilities))
                
                return {
                    'classification': classification,
                    'confidence': round(confidence, 3),
                    'features': features,
                    'method': 'ml'
                }
            except Exception as e:
                logger.error(f"ML prediction failed: {e}")
                # Fall through to rule-based
        
        # Fallback to rule-based (FR-10-07)
        return cls._rule_based_predict(features)
    
    @classmethod
    def _rule_based_predict(cls, features):
        """Rule-based fallback prediction (FR-10-07)."""
        accuracy = features['accuracy']
        attempts = features['attempts']
        recent_accuracy = features['recent_accuracy']
        
        if accuracy >= 75 and attempts >= 10 and recent_accuracy >= 65:
            classification = 'Strong'
            confidence = 0.8
        elif accuracy < 50 or (attempts >= 5 and recent_accuracy < 40):
            classification = 'Weak'
            confidence = 0.75
        else:
            classification = 'Moderate'
            confidence = 0.7
        
        return {
            'classification': classification,
            'confidence': confidence,
            'features': features,
            'method': 'rule-based'
        }


class WeakAreaDetector:
    """Detect weak areas and recommend topics using ML."""
    
    @staticmethod
    def update_user_performance(user):
        """
        Update ML predictions for all topics a user has practiced.
        
        Returns:
            int: Number of topics updated
        """
        from .models import TopicPerformance
        
        # Get all topics the user has practiced
        topics = Topic.objects.filter(
            questions__practice_attempts__session__user=user
        ).distinct()
        
        updated_count = 0
        
        for topic in topics:
            prediction = PerformancePredictor.predict(user, topic)
            
            if prediction is None:
                continue
            
            features = prediction['features']
            classification = prediction['classification']
            confidence = prediction['confidence']
            
            # Calculate priority (higher = more urgent)
            priority = WeakAreaDetector._calculate_priority(
                classification, features
            )
            
            TopicPerformance.objects.update_or_create(
                user=user,
                topic=topic,
                defaults={
                    'accuracy': features['accuracy'],
                    'attempts': features['attempts'],
                    'avg_time': features['avg_time'],
                    'easy_accuracy': features['easy_accuracy'],
                    'medium_accuracy': features['medium_accuracy'],
                    'hard_accuracy': features['hard_accuracy'],
                    'classification': classification,
                    'confidence': confidence,
                    'priority': priority,
                }
            )
            updated_count += 1
        
        logger.info(f"Updated {updated_count} topic performances for {user.email}")
        return updated_count
    
    @staticmethod
    def _calculate_priority(classification, features):
        """Calculate priority score (higher = more urgent)."""
        base_priority = {
            'Weak': 100,
            'Moderate': 50,
            'Strong': 10,
        }.get(classification, 30)
        
        # Higher priority for declining trend
        if features['recent_accuracy'] < features['accuracy']:
            base_priority += 20
        
        # Lower priority for strong with high recent accuracy
        if classification == 'Strong' and features['recent_accuracy'] >= 80:
            base_priority -= 10
        
        return max(0, base_priority)
    
    @staticmethod
    def get_weak_topics(user, limit=5):
        """
        Get the top N weakest topics for a user.
        
        Returns:
            QuerySet of TopicPerformance objects
        """
        from .models import TopicPerformance
        
        return TopicPerformance.objects.filter(
            user=user,
            classification__in=['Weak', 'Moderate']
        ).select_related(
            'topic__chapter__subject'
        ).order_by('-priority')[:limit]
    
    @staticmethod
    def get_recommended_topic(user):
        """
        Get the next best topic to practice.
        
        Returns:
            Topic or None
        """
        from .models import TopicPerformance
        
        # First priority: Weak topics
        weak = TopicPerformance.objects.filter(
            user=user,
            classification='Weak'
        ).select_related('topic').order_by('-priority').first()
        
        if weak:
            return weak.topic
        
        # Second priority: Moderate topics with poor recent trend
        moderate = TopicPerformance.objects.filter(
            user=user,
            classification='Moderate'
        ).select_related('topic').order_by('-priority').first()
        
        if moderate:
            return moderate.topic
        
        return None