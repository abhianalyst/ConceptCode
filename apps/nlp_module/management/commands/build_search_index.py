from django.core.management.base import BaseCommand
from apps.nlp_module.services import ContentIndexer


class Command(BaseCommand):
    help = 'Build the semantic search index (Sentence-BERT + FAISS)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--no-progress',
            action='store_true',
            help='Disable progress bar'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('BUILDING SEMANTIC SEARCH INDEX'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        try:
            stats = ContentIndexer.build_index(
                show_progress=not options['no_progress']
            )
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(
                f"✅ Indexed {stats['count']} content items"
            ))
            self.stdout.write(self.style.SUCCESS(
                f"📐 Embedding dimension: {stats['dimension']}"
            ))
            self.stdout.write(self.style.SUCCESS(
                f"💾 Saved to: apps/nlp_module/vector_store/"
            ))
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Search is now ready! 🎉'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())