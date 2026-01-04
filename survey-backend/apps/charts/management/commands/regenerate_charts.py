"""
Management command to regenerate charts for a dataset.
Usage: python manage.py regenerate_charts <dataset_uid>
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.ingest.models import UploadedDataset
from apps.charts.models import ChartSpec
from apps.charts.services import generate_taam_chart_specs, generate_generic_chart_specs
from apps.ingest.services import parse_uploaded_file, is_taam_dataset


class Command(BaseCommand):
    help = 'Regenerate charts for a specific dataset'

    def add_arguments(self, parser):
        parser.add_argument('dataset_uid', type=str, help='UID of the dataset to regenerate charts for')

    def handle(self, *args, **options):
        dataset_uid = options['dataset_uid']
        
        try:
            dataset = UploadedDataset.objects.get(uid=dataset_uid)
        except UploadedDataset.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Dataset with UID {dataset_uid} not found'))
            return
        
        self.stdout.write(f'Regenerating charts for: {dataset.filename}')
        
        # Delete existing charts
        deleted_count = ChartSpec.objects.filter(dataset=dataset).count()
        ChartSpec.objects.filter(dataset=dataset).delete()
        self.stdout.write(self.style.WARNING(f'Deleted {deleted_count} existing charts'))
        
        # Parse file
        df, _, error = parse_uploaded_file(dataset.storage_path)
        
        if error:
            self.stdout.write(self.style.ERROR(f'Error parsing file: {error}'))
            return
        
        # Determine if TAAM dataset
        is_taam = is_taam_dataset(df)
        self.stdout.write(f'Dataset type: {"TAAM" if is_taam else "Generic"}')
        
        # Generate chart specs
        if is_taam:
            chart_specs_data = generate_taam_chart_specs(df, dataset.id, dataset.owner.id)
        else:
            chart_specs_data = generate_generic_chart_specs(df, dataset.id, dataset.owner.id)
        
        self.stdout.write(f'Generated {len(chart_specs_data)} chart specifications')
        
        # Create ChartSpec objects
        with transaction.atomic():
            chart_objects = [
                ChartSpec(
                    owner=dataset.owner,
                    dataset=dataset,
                    chart_type=spec_data['chart_type'],
                    chart_config=spec_data['chart_config'],
                    is_canonical=spec_data['is_canonical'],
                    derived_metrics=spec_data['derived_metrics'],
                )
                for spec_data in chart_specs_data
            ]
            
            ChartSpec.objects.bulk_create(chart_objects, batch_size=500)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(chart_specs_data)} charts'))
        self.stdout.write(self.style.SUCCESS('✓ Charts regenerated successfully!'))
