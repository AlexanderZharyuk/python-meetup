import logging
import os

from enum import Enum

import django

from more_itertools import chunked

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from menu_blocks import start_block, programs_block, performance_block

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


class ConversationPoints(Enum):
    MENU = 0
    PROGRAM_SCHEDULE = 1
    PROGRAM_DESCRIPTION = 2
    EXIT_FROM_DESCRIPTION = 3
    CHOOSE_PROGRAM_FOR_QUESTION = 4
    PERFORMANCE_SPEAKERS = 5
    CHOOSE_PERFORMANCE_SPEAKER = 6
    QUESTION_FOR_SPEAKER = 7


def setup_admin_panel() -> None:
    os.environ["DJANGO_SETTINGS_MODULE"] = 'bot_settings'
    django.setup()


def start(update: Update, context: CallbackContext) -> int:
    start_block(update=update)
    return ConversationPoints.MENU.value


def program(update: Update, context: CallbackContext) -> int:
    programs_block(update=update)
    return ConversationPoints.PROGRAM_SCHEDULE.value


def schedules(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text

    if user_choice == "Главное меню":
        start_block(update=update)
        return ConversationPoints.MENU.value

    if user_choice == "Назад":
        from admin_panel.Conference.models import Performance
        schedules = Performance.objects.filter(
            conference__name_conf=context.user_data["performance"]
        )
        performances, text = performance_block(update, schedules, context)

        reply_keyboard = list(chunked(performances, 2))
        update.message.reply_text(
            text=text,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        return ConversationPoints.PROGRAM_DESCRIPTION.value

    from admin_panel.Conference.models import Performance
    performances = []
    performances_in_conference = Performance.objects.filter(
        conference__name_conf=user_choice
    )
    for perforamnce_id, performance in enumerate(performances_in_conference,
                                                 start=1):
        performance_name = performance.performance_name
        performance_time = performance.time_performance
        performance = f'{perforamnce_id}. {performance_name}\n' \
                      f'Время: {performance_time}\n\n'
        performances.append(performance)

    text = f"У программы «{user_choice}» будут следующие выступления:\n\n" \
           f"{''.join(performances)}\n" \
           f"Про какое выступление вам бы хотелось узнать побольше?"

    performances = [performance.performance_name for performance in
                    performances_in_conference]
    performances.append("Назад")

    reply_keyboard = list(chunked(performances, 2))
    update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    context.user_data["performance"] = user_choice
    return ConversationPoints.PROGRAM_DESCRIPTION.value


def get_program_description(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text

    if user_choice == "Назад":
        programs_block(update=update)
        return ConversationPoints.PROGRAM_SCHEDULE.value

    from admin_panel.Conference.models import Performance
    reply_keyboard = [["Главное меню", "Назад"]]
    performance = Performance.objects.get(performance_name=user_choice)
    update.message.reply_text(
        f"Описание программы: {performance.description}\n\n"
        f"Спикер программы: {performance.speaker}",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    return ConversationPoints.EXIT_FROM_DESCRIPTION.value


def question_for_speaker(update: Update, context: CallbackContext) -> int:
    from admin_panel.Conference.models import Conference
    programs = [conference.name_conf for conference in
                Conference.objects.all()]
    programs.append("Главное меню")

    update.message.reply_text(
        "Спикеру какой программы у вас есть вопрос?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=list(chunked(programs, 2)),
            one_time_keyboard=True,
            resize_keyboard=True
        ),
    )
    return ConversationPoints.CHOOSE_PROGRAM_FOR_QUESTION.value


def get_performance_times(update: Update, context: CallbackContext) -> int:
    from admin_panel.Conference.models import Conference
    conferences = Conference.objects.filter(
        name_conf=update.message.text
    )
    for conference in conferences:
        performances = conference.performances.all()

    reply_keyboard = [str(performance.time_performance) for performance
                      in performances]
    context.user_data["performance"] = update.message.text

    update.message.reply_text(
        "Когда было выступление?",
         reply_markup=ReplyKeyboardMarkup(
             keyboard=list(chunked(reply_keyboard, 2)),
             one_time_keyboard=True,
             resize_keyboard=True
         )
    )
    return ConversationPoints.PERFORMANCE_SPEAKERS.value


def get_performance_speakers(update: Update, context: CallbackContext) -> int:
    context.user_data["time"] = update.message.text
    from admin_panel.Conference.models import Performance
    performances = Performance.objects.filter(
        time_performance=context.user_data['time']
    )

    speakers = [str(performance.speaker) for performance in performances]
    reply_keyboard = list(chunked(speakers, 1))
    reply_keyboard.append(["Назад"])
    update.message.reply_text(
        text=f"На программе «{context.user_data['performance']}» в "
             f"{context.user_data['time']} выступал:\n\n",
        reply_markup=ReplyKeyboardMarkup(
             keyboard=reply_keyboard,
             one_time_keyboard=True,
             resize_keyboard=True
         )
    )
    return ConversationPoints.QUESTION_FOR_SPEAKER.value


def question(update: Update, context: CallbackContext) -> int:
    if update.message.text == "Назад":
        from admin_panel.Conference.models import Conference
        programs = [conference.name_conf for conference in
                    Conference.objects.all()]
        programs.append("Главное меню")

        update.message.reply_text(
            "Спикеру какой программы у вас есть вопрос?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=list(chunked(programs, 2)),
                one_time_keyboard=True,
                resize_keyboard=True
            ),
        )
        return ConversationPoints.CHOOSE_PROGRAM_FOR_QUESTION.value

    update.message.reply_text(
        text=f"Задайте свой вопрос:"
    )
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    load_dotenv()

    telegram_bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    updater = Updater(telegram_bot_token)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)
        ],
        states={
            ConversationPoints.MENU.value: [
                MessageHandler(
                    Filters.regex('^(📆 Программа)$'),
                    program
                ),
                MessageHandler(
                    Filters.regex('^(❔Задать вопрос спикеру)$'),
                    question_for_speaker
                )
            ],
            ConversationPoints.PROGRAM_SCHEDULE.value: [
                MessageHandler(
                    Filters.text,
                    schedules
                )
            ],
            ConversationPoints.PROGRAM_DESCRIPTION.value: [
                MessageHandler(
                    Filters.text,
                    get_program_description
                )
            ],
            ConversationPoints.EXIT_FROM_DESCRIPTION.value: [
                MessageHandler(
                    Filters.regex('^(Главное меню)$'),
                    start
                ),
                MessageHandler(
                    Filters.regex('^(Назад)$'),
                    schedules
                ),
            ],
            ConversationPoints.CHOOSE_PROGRAM_FOR_QUESTION.value: [
                MessageHandler(
                    Filters.regex('^(Главное меню)$'),
                    start
                ),
                MessageHandler(
                    Filters.text,
                    get_performance_times
                ),
            ],
            ConversationPoints.PERFORMANCE_SPEAKERS.value: [
                MessageHandler(
                    Filters.text,
                    get_performance_speakers
                ),
            ],
            ConversationPoints.QUESTION_FOR_SPEAKER.value: [
                MessageHandler(
                    Filters.text,
                    question
                ),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    setup_admin_panel()
    from admin_panel.Conference.models import Performance, Conference, Speaker
    main()
