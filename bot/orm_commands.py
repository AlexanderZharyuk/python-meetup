import os

import django

from telegram import Update
from telegram.ext import CallbackContext


os.environ["DJANGO_SETTINGS_MODULE"] = 'bot_settings'
django.setup()

from admin_panel.Conference.models import (
    Conference,
    Performance,
    Speaker,
    Question
)


def get_programs_list() -> list:
    programs = [conference.name for conference
                in Conference.objects.all()]
    return programs


def get_performances_list(context: CallbackContext, user_choice=None) -> list:
    if user_choice:
        performances = Performance.objects.filter(
            conference__name=user_choice
        )
        return performances

    performances = Performance.objects.filter(
        conference__name=context.user_data["performance"]
    )
    return performances


def get_performance(user_choice: str) -> Performance:
    performance = Performance.objects.get(name=user_choice)
    return performance


def get_performances_in_conference(update: Update):
    conference = Conference.objects.get(
        name=update.message.text
    )
    performances = conference.performances.all()
    return performances


def get_performance_by_time(time: str, performance_name: str) -> Performance:
    performance = Performance.objects.get(
        time=time,
        conference__name=performance_name
    )
    return performance


def get_speaker_telegram_id(speaker_fullname: str) -> str:
    speaker = Speaker.objects.get(fullname=speaker_fullname)
    return speaker.telegram_id


def get_speaker_by_telegam_id(user_id: str) -> Speaker:
    speaker = Speaker.objects.get(telegram_id=user_id)
    return speaker


def save_question(by_user: str, question: str, speaker_id: str) -> None:
    speaker = get_speaker_by_telegam_id(user_id=speaker_id)
    Question.objects.create(
        telegram_user_id=by_user,
        question=question,
        speaker=speaker
    )


def get_user_answer_id(speaker_id: str,
                       question_text: str) -> str:
    speaker = get_speaker_by_telegam_id(user_id=speaker_id)
    question = Question.objects.get(
        speaker=speaker,
        question=question_text
    )
    return question.telegram_user_id


def get_speakers_ids() -> list:
    speakers_ids = [speaker.telegram_id for speaker
                    in Speaker.objects.all()]
    return speakers_ids

