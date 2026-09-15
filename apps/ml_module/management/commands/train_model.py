from django.core.management.base import BaseCommand
from apps.ml_module.services import ModelTrainer


class Command(BaseCommand):
    help = 'Train the ML models for weak area detection'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('ML MODEL TRAINING'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        results = ModelTrainer.train_models()
        
        self.stdout.write('\n📊 Training Results:\n')
        
        # Decision Tree
        dt = results['decision_tree']
        self.stdout.write(self.style.SUCCESS(
            f"🌳 Decision Tree Accuracy: {dt['accuracy']}%"
        ))
        self.stdout.write(f"   Saved to: {dt['model_path']}\n")
        
        # Random Forest
        rf = results['random_forest']
        self.stdout.write(self.style.SUCCESS(
            f"🌲 Random Forest Accuracy: {rf['accuracy']}%"
        ))
        self.stdout.write(f"   Saved to: {rf['model_path']}\n")
        
        self.stdout.write('\n📈 Feature Importance (Random Forest):')
        for feature, importance in sorted(
            rf['feature_importance'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            bar = '█' * int(importance * 50)
            self.stdout.write(f"   {feature:20} {importance:.4f} {bar}")
        
        self.stdout.write(self.style.SUCCESS('\n✅ Training complete!'))