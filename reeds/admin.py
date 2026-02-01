from django.contrib import admin
from .models import Reed, UsageSession, QualitySnapshot, Modification


class UsageSessionInline(admin.TabularInline):
    model = UsageSession
    extra = 0
    fields = ('start_time', 'end_time', 'duration_minutes', 'context')
    readonly_fields = ('duration_minutes',)


class QualitySnapshotInline(admin.TabularInline):
    model = QualitySnapshot
    extra = 0
    fields = ('timestamp', 'overall_rating', 'tone_quality', 'response', 'intonation')


class ModificationInline(admin.TabularInline):
    model = Modification
    extra = 0
    fields = ('timestamp', 'modification_type', 'goal', 'success_rating')


@admin.register(Reed)
class ReedAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_date', 'total_play_time_minutes', 'cane_source')
    list_filter = ('status', 'created_date', 'cane_source')
    search_fields = ('name', 'notes', 'cane_source')
    readonly_fields = ('total_play_time_minutes',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'status', 'created_date', 'total_play_time_minutes')
        }),
        ('Construction Details', {
            'fields': ('cane_source', 'shape', 'gouge_thickness')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    inlines = [UsageSessionInline, QualitySnapshotInline, ModificationInline]


@admin.register(UsageSession)
class UsageSessionAdmin(admin.ModelAdmin):
    list_display = ('reed', 'start_time', 'end_time', 'duration_minutes', 'context')
    list_filter = ('context', 'start_time')
    search_fields = ('reed__name', 'notes', 'context')
    readonly_fields = ('duration_minutes',)
    
    fieldsets = (
        ('Session Details', {
            'fields': ('reed', 'start_time', 'end_time', 'duration_minutes')
        }),
        ('Context', {
            'fields': ('context', 'notes')
        }),
    )


@admin.register(QualitySnapshot)
class QualitySnapshotAdmin(admin.ModelAdmin):
    list_display = ('reed', 'timestamp', 'overall_rating', 'tone_quality', 'response', 'intonation')
    list_filter = ('timestamp',)
    search_fields = ('reed__name', 'notes')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('reed', 'timestamp')
        }),
        ('Quality Ratings', {
            'fields': ('overall_rating', 'tone_quality', 'response', 'intonation', 'stability', 'ease_of_playing')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(Modification)
class ModificationAdmin(admin.ModelAdmin):
    list_display = ('reed', 'timestamp', 'modification_type', 'goal', 'success_rating')
    list_filter = ('modification_type', 'timestamp')
    search_fields = ('reed__name', 'description', 'goal')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('reed', 'timestamp', 'modification_type')
        }),
        ('Details', {
            'fields': ('description', 'goal', 'success_rating')
        }),
    )

