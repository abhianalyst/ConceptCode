# apps/practice/management/commands/test_adaptive.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import Topic
from apps.practice.adaptive import AdaptiveDifficulty

User = get_user_model()


class Command(BaseCommand):
    help = 'Test the adaptive difficulty system'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='User email')
        parser.add_argument('--topic', type=int, help='Topic ID')

    def handle(self, *args, **options):
        user_email = options.get('user')
        topic_id = options.get('topic')
        
        if not user_email:
            self.stdout.write(self.style.ERROR('Please provide --user'))
            return
        
        if not topic_id:
            self.stdout.write(self.style.ERROR('Please provide --topic'))
            return
        
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User not found: {user_email}'))
            return
        
        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Topic not found: {topic_id}'))
            return
        
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('ADAPTIVE DIFFICULTY TEST'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        
        adaptive = AdaptiveDifficulty(user, topic)
        
        # Show performance summary
        self.stdout.write(f'\n📊 Performance Summary for: {user.email}')
        self.stdout.write(f'   Topic: {topic.name}')
        self.stdout.write('')
        
        for level in adaptive.DIFFICULTY_LEVELS:
            data = adaptive.performance.get(level, {})
            self.stdout.write(f'   {level}:')
            self.stdout.write(f'      Attempts: {data.get("total", 0)}')
            self.stdout.write(f'      Correct: {data.get("correct", 0)}')
            self.stdout.write(f'      Accuracy: {data.get("accuracy", 0)}%')
        
        self.stdout.write('')
        self.stdout.write(f'🎯 Current Level: {adaptive.current_level}')
        self.stdout.write(f'🤖 Next Difficulty: {adaptive.get_next_difficulty()}')
        self.stdout.write(f'📈 Adaptive Mode: {"ON" if adaptive.should_use_adaptive() else "OFF (need more data)"}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Test completed!'))