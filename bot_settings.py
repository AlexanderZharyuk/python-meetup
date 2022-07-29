from admin_panel.Meetup.settings import *

INSTALLED_APPS[INSTALLED_APPS.index('Conference')] = 'admin_panel.Conference'

USING_TG_BOT_SETTINGS = True
