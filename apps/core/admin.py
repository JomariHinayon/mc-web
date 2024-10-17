from django.contrib import admin
from .models import Video

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'source_type', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'youtube_url')
    list_filter = ('source_type', 'user')
    ordering = ('-created_at',)

admin.site.register(Video, VideoAdmin)