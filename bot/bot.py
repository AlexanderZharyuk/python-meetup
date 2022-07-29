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
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          "admin_panel.Meetup.settings")
    django.setup()


def start(update: Update, context: CallbackContext) -> int:
    start_block(update=update)
    return ConversationPoints.MENU.value


def program(update: Update, context: CallbackContext) -> int:
    programs_block(update=update)
    return ConversationPoints.PROGRAM_SCHEDULE.value


def schedules(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text
    schedules = [
        {
            "time": "09:00",
            "performance_name": "Регистрация"
        },
        {
            "time": "10:00",
            "performance_name": "Первое выступление"
        },
        {
            "time": "10:30",
            "performance_name": "Второе выступление"
        },
    ]

    if user_choice == "Главное меню":
        start_block(update=update)
        return ConversationPoints.MENU.value

    if user_choice == "Назад":
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

    performances = []
    for perforamnce_id, performance in enumerate(schedules, start=1):
        performance_name = performance["performance_name"]
        performance_time = performance["time"]
        performance = f'{perforamnce_id}.{performance_name}\n' \
                      f'Время: {performance_time}\n'
        performances.append(performance)

    text = f"У программы {user_choice} будут следующие выступления:\n\n" \
           f"{''.join(performances)}\n" \
           f"Про какое выступление вам бы хотелось узнать побольше?"

    performances = [performance["performance_name"] for performance in
                    schedules]
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
        programs = [f'Программа №{program}' for program in range(1, 4)]
        programs_text = [f"{program_number}. {program}\n" for
                         program_number, program in
                         enumerate(programs, start=1)]
        programs.append("Главное меню")

        update.message.reply_text(
            'Сегодня у нас проходят следующие программы:\n\n'
            f'{"".join(programs_text)}\n\n'
            f'Какая программа вас заинтересовала?',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=list(chunked(programs, 2)),
                one_time_keyboard=True,
                resize_keyboard=True
            ),
        )
        return ConversationPoints.PROGRAM_SCHEDULE.value

    reply_keyboard = [["Главное меню", "Назад"]]
    update.message.reply_text(
        f"Описание программы {user_choice}",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    return ConversationPoints.EXIT_FROM_DESCRIPTION.value


def question_for_speaker(update: Update, context: CallbackContext) -> int:
    programs = [f'Программа №{program}' for program in range(1, 4)]
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
    reply_keyboard = [["12:00", "14:00"]]
    context.user_data["performance"] = update.message.text

    update.message.reply_text(
        "Когда было выступление?",
         reply_markup=ReplyKeyboardMarkup(
             keyboard=reply_keyboard,
             one_time_keyboard=True,
             resize_keyboard=True
         )
    )
    return ConversationPoints.PERFORMANCE_SPEAKERS.value


def get_performance_speakers(update: Update, context: CallbackContext) -> int:
    context.user_data["time"] = update.message.text
    speakers = [f"{speaker_number}. Выступающий #{speaker_number}\n" for speaker_number in range(1, 5)]
    reply_keyboard = list(chunked(speakers, 1))
    reply_keyboard.append(["Назад"])
    update.message.reply_text(
        text=f"На программе {context.user_data['performance']} в "
             f"{context.user_data['time']} выступали:\n\n",
        reply_markup=ReplyKeyboardMarkup(
             keyboard=reply_keyboard,
             one_time_keyboard=True,
             resize_keyboard=True
         )
    )
    return ConversationPoints.QUESTION_FOR_SPEAKER.value


def question(update: Update, context: CallbackContext) -> int:
    if update.message.text == "Назад":
        programs = [f'Программа №{program}' for program in range(1, 4)]
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
    setup_admin_panel()
    from admin_panel.Conference.models import Speaker, Performance


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
    main()
