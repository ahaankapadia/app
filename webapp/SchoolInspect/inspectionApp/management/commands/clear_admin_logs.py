from django.core.management.base import BaseCommand
from django.contrib.admin.models import LogEntry
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Clear Django admin logs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=0,
            help='Number of days of logs to retain (default is 30).'
        )

    def handle(self, *args, **options):
        days_to_retain = options['days']
        cutoff_date = timezone.now() - timedelta(days=days_to_retain)
        
        deleted_count, _ = LogEntry.objects.filter(action_time__lt=cutoff_date).delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} admin log entries older than {days_to_retain} days.'))
