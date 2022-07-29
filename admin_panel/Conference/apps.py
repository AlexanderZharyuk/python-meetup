from django.apps import AppConfig
from django.conf import settings


class ConferenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'

    if hasattr(settings, 'USING_TG_BOT_SETTINGS') and settings.USING_TG_BOT_SETTINGS:
        name = 'admin_panel.Conference'
    else:
        name = "Conference"
