import os

import django


os.environ["DJANGO_SETTINGS_MODULE"] = 'bot_settings'
django.setup()

from admin_panel.Conference.models import Conference, Performance, Speaker


def get_programs_list() -> list:
    programs = [conference.name_conf for conference
                in Conference.objects.all()]
    return programs


def get_performances_list(context, user_choice=None) -> list:
    if user_choice:
        performances = Performance.objects.filter(
            conference__name_conf=user_choice
        )
        return performances

    performances = Performance.objects.filter(
        conference__name_conf=context.user_data["performance"]
    )
    return performances


def get_performance(user_choice: str):
    performance = Performance.objects.get(performance_name=user_choice)
    return performance


def get_performances_in_conference(update):
    conference = Conference.objects.get(
        name_conf=update.message.text
    )
    performances = conference.performances.all()
    return performances


def get_performance_by_time(time):
    performance = Performance.objects.get(
        time_performance=time
    )
    return performance
