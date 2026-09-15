from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.ml_module.services import (
    PerformancePredictor,
    WeakAreaDetector,
    FeatureExtractor
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Test ML predictions for a user'
    
    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='User email')
    
    def handle(self, *args, **options):
        user_email = options.get('user')
        
        if not user_email:
            self.stdout.write(self.style.ERROR('Please provide --user'))
            return
        
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User not found: {user_email}'))
            return
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'ML PREDICTIONS FOR: {user.email}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Update all performances
        count = WeakAreaDetector.update_user_performance(user)
        self.stdout.write(f'\n✅ Updated {count} topic performances\n')
        
        # Show weak topics
        weak_topics = WeakAreaDetector.get_weak_topics(user, limit=5)
        
        if weak_topics:
            self.stdout.write('⚠️  Top Weak Areas:')
            for perf in weak_topics:
                self.stdout.write(
                    f"   • {perf.topic.name[:40]:40} "
                    f"| {perf.classification:8} "
                    f"| Accuracy: {perf.accuracy:.1f}% "
                    f"| Priority: {perf.priority}"
                )
        else:
            self.stdout.write('✅ No weak areas detected!')
        
        # Show recommendation
        recommended = WeakAreaDetector.get_recommended_topic(user)
        if recommended:
            self.stdout.write(self.style.SUCCESS(
                f'\n🎯 Recommended Next Topic: {recommended.name}'
            ))