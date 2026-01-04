"""
Signal handlers for the ingest app.
"""
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import UploadedDataset


@receiver(post_delete, sender=UploadedDataset)
def delete_dataset_file(sender, instance, **kwargs):
    """
    Delete the physical file when a dataset is deleted.
    """
    if instance.storage_path and os.path.exists(instance.storage_path):
        try:
            os.remove(instance.storage_path)
            print(f"Deleted file: {instance.storage_path}")
        except Exception as e:
            print(f"Error deleting file {instance.storage_path}: {e}")
