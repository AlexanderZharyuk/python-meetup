from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Speaker, Conference, Performance


# Register your models here.
@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ['tg_speaker_id', 'fullname']


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ['name_conf', 'date']


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ['performance_name', 'time_performance', 'speaker',
                    'conference']
    list_filter = ['conference']


admin.site.unregister(User)
admin.site.unregister(Group)
