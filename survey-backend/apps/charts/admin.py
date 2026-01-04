from django.contrib import admin
from .models import ChartSpec, UserSelection


@admin.register(ChartSpec)
class ChartSpecAdmin(admin.ModelAdmin):
    list_display = ('chart_type', 'owner', 'dataset', 'is_canonical', 'created_at')
    list_filter = ('chart_type', 'is_canonical', 'created_at')
    search_fields = ('owner__email', 'dataset__filename')
    readonly_fields = ('uid', 'created_at', 'updated_at')


@admin.register(UserSelection)
class UserSelectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'dataset', 'selected_chart', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'dataset__filename')
    readonly_fields = ('uid', 'created_at', 'updated_at')
