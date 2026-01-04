"""
Models for data ingestion and file upload management.
"""
from django.db import models
from django.conf import settings
from config.models import TimeStampedBaseModel


class UploadedDataset(TimeStampedBaseModel):
    """
    Stores metadata about uploaded CSV/XLSX files.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_datasets',
        help_text="User who uploaded this dataset"
    )
    filename = models.CharField(
        max_length=255,
        help_text="Original filename"
    )
    mime_type = models.CharField(
        max_length=100,
        help_text="MIME type of the uploaded file"
    )
    size_bytes = models.BigIntegerField(
        help_text="File size in bytes"
    )
    storage_path = models.CharField(
        max_length=500,
        help_text="Path where the file is stored"
    )
    original_headers = models.JSONField(
        default=list,
        help_text="Original column headers from the file"
    )
    row_count = models.IntegerField(
        default=0,
        help_text="Number of data rows (excluding header)"
    )
    parsed_ok = models.BooleanField(
        default=False,
        help_text="Whether the file was successfully parsed"
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if parsing failed"
    )

    class Meta:
        db_table = 'uploaded_datasets'
        ordering = ['-created_at']
        verbose_name = 'Uploaded Dataset'
        verbose_name_plural = 'Uploaded Datasets'
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['parsed_ok']),
        ]

    def __str__(self):
        return f"{self.filename} by {self.owner.email}"


class ParsedRecord(models.Model):
    """
    Stores individual rows from parsed datasets.
    Optional: Can be used for smaller datasets or samples.
    For large datasets, consider storing only profiled schema.
    """
    id = models.BigAutoField(primary_key=True)
    dataset = models.ForeignKey(
        UploadedDataset,
        on_delete=models.CASCADE,
        related_name='parsed_records',
        help_text="Dataset this record belongs to"
    )
    row_index = models.IntegerField(
        help_text="Row number in the original file (0-indexed)"
    )
    data = models.JSONField(
        help_text="JSON representation of the row data"
    )

    class Meta:
        db_table = 'parsed_records'
        ordering = ['dataset', 'row_index']
        verbose_name = 'Parsed Record'
        verbose_name_plural = 'Parsed Records'
        indexes = [
            models.Index(fields=['dataset', 'row_index']),
        ]
        unique_together = [['dataset', 'row_index']]

    def __str__(self):
        return f"Row {self.row_index} of {self.dataset.filename}"
