import csv
from django.core.management.base import BaseCommand
from inspectionApp.models import Inspection

class Command(BaseCommand):
    help = 'Import data from JotForm CSV export'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to the JotForm CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file']
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Map JotForm fields to Inspection model fields
                Inspection.objects.create(
                    sf_code=row['sf_code'],
                    school_name=row['school_name'],
                    inspector_name=row['inspector_name'],
                    # Add other fields as necessary
                )
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
