import logging
import os

from enum import Enum

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
from orm_commands import (
    get_performances_list,
    get_performance,
    get_programs_list,
    get_performances_in_conference,
    get_performance_by_time
)

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
        performances_list = get_performances_list(context=context)
        performances, text = performance_block(
            context=context,
            performances_list=performances_list,
            user_is_back=True
        )

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

    performances_list = get_performances_list(
        context=context,
        user_choice=user_choice
    )

    performances, text = performance_block(
        context=context,
        performances_list=performances_list,
        user_choice=user_choice
    )

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

    reply_keyboard = [["Главное меню", "Назад"]]
    performance = get_performance(user_choice=user_choice)
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
    programs = get_programs_list()
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
    performances = get_performances_in_conference(update=update)
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
    performance = get_performance_by_time(time=context.user_data['time'])
    speaker = performance.speaker.fullname
    reply_keyboard = [[speaker], ["Назад"]]
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
        programs = get_programs_list()
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
    main()
