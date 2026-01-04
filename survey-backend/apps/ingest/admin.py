from django.contrib import admin
from .models import UploadedDataset, ParsedRecord


@admin.register(UploadedDataset)
class UploadedDatasetAdmin(admin.ModelAdmin):
    list_display = ('filename', 'owner', 'row_count', 'parsed_ok', 'created_at')
    list_filter = ('parsed_ok', 'created_at')
    search_fields = ('filename', 'owner__email')
    readonly_fields = ('uid', 'created_at', 'updated_at')


@admin.register(ParsedRecord)
class ParsedRecordAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'row_index', 'id')
    list_filter = ('dataset',)
    search_fields = ('dataset__filename',)
