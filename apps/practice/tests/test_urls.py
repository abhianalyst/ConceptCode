from django.test import TestCase
from django.urls import reverse

class URLNameTests(TestCase):
    def test_all_practice_urls_reverse(self):
        """Ensure every named URL can be reversed."""
        from apps.practice.models import Topic
        from apps.core.models import Subject, Chapter

        # Create minimal fixtures
        subj = Subject.objects.create(name="Bio", is_active=True)
        chap = Chapter.objects.create(subject=subj, name="Cell", is_active=True, unit_number=1)
        topic = Topic.objects.create(chapter=chap, name="Division", is_active=True)

        urls_to_test = [
            ('practice:analytics', {}),
            ('practice:create-practice-session', {'topic_id': topic.id}),
            ('practice:practice-session', {'session_id': 1}),
            # ... add all
        ]
        for name, kwargs in urls_to_test:
            with self.subTest(url=name):
                self.assertTrue(reverse(name, kwargs=kwargs))