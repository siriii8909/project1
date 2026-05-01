from django.contrib import admin
from .models import Detection

@admin.register(Detection)
class DetectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'crop_type', 'disease', 'confidence', 'created_at')
    list_filter = ('crop_type', 'disease', 'created_at', 'user')
    search_fields = ('crop_type', 'disease', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)
