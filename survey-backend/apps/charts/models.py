"""
Models for chart specifications and user selections.
"""
from django.db import models
from django.conf import settings
from config.models import TimeStampedBaseModel


class ChartType(models.TextChoices):
    """Chart type choices"""
    TAAM_RADAR = 'taam_radar', 'TAAM Radar'
    PERSONA_DISTRIBUTION = 'persona_distribution', 'Persona Distribution'
    BAR = 'bar', 'Bar Chart'
    LINE = 'line', 'Line Chart'
    PIE = 'pie', 'Pie Chart'
    SCATTER = 'scatter', 'Scatter Plot'
    HEATMAP = 'heatmap', 'Heatmap'


class ChartSpec(TimeStampedBaseModel):
    """
    Stores chart specifications and configurations.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chart_specs',
        help_text="User who owns this chart"
    )
    dataset = models.ForeignKey(
        'ingest.UploadedDataset',
        on_delete=models.CASCADE,
        related_name='chart_specs',
        help_text="Dataset this chart is based on"
    )
    chart_type = models.CharField(
        max_length=20,
        choices=ChartType.choices,
        help_text="Type of chart"
    )
    chart_config = models.JSONField(
        default=dict,
        help_text="Chart configuration (axes, series, labels, colors, etc.)"
    )
    is_canonical = models.BooleanField(
        default=False,
        help_text="For TAAM: whether this is the canonical persona radar"
    )
    derived_metrics = models.JSONField(
        default=dict,
        help_text="Derived metrics (distributions, heatmaps, overlay vectors, etc.)"
    )

    class Meta:
        db_table = 'chart_specs'
        ordering = ['-created_at']
        verbose_name = 'Chart Specification'
        verbose_name_plural = 'Chart Specifications'
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['dataset']),
            models.Index(fields=['chart_type']),
        ]

    def __str__(self):
        return f"{self.chart_type} for {self.dataset.filename}"


class UserSelection(TimeStampedBaseModel):
    """
    Stores user's selected chart for a dataset.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chart_selections',
        help_text="User who made the selection"
    )
    dataset = models.ForeignKey(
        'ingest.UploadedDataset',
        on_delete=models.CASCADE,
        related_name='user_selections',
        help_text="Dataset for this selection"
    )
    selected_chart = models.ForeignKey(
        ChartSpec,
        on_delete=models.CASCADE,
        related_name='selections',
        help_text="The selected chart"
    )
    note = models.TextField(
        blank=True,
        help_text="Optional note about the selection"
    )

    class Meta:
        db_table = 'user_selections'
        ordering = ['-created_at']
        verbose_name = 'User Selection'
        verbose_name_plural = 'User Selections'
        indexes = [
            models.Index(fields=['user', 'dataset']),
        ]
        unique_together = [['user', 'dataset']]

    def __str__(self):
        return f"{self.user.email} selected {self.selected_chart.chart_type}"
