from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from more_itertools import chunked


def start_block(update):
    reply_keyboard = [['📆 Программа', '❔Задать вопрос спикеру']]

    update.message.reply_text(
        'Здравствуйте! Это официальный бот PythonMeetup.\n\n'
        'Здесь вы можете ознакомиться с сегодняшними программами, '
        'их расписаниями, а также задать интересующий вопрос спикеру!',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        ),
    )


def programs_block(update):
    programs = [f'Программа №{program}' for program in range(1, 4)]
    programs_text = [f"{program_number}. {program}\n" for
                     program_number, program in enumerate(programs, start=1)]
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


def performance_block(update, schedules, context):
    performances = []
    for perforamnce_id, performance in enumerate(schedules, start=1):
        performance_name = performance["performance_name"]
        performance_time = performance["time"]
        performance = f'{perforamnce_id}.{performance_name}\n' \
                      f'Время: {performance_time}\n'
        performances.append(performance)
    text = f"У программы {context.user_data['performance']} " \
           f"будут следующие выступления:\n\n" \
           f"{''.join(performances)}\n" \
           f"Про какое выступление вам бы хотелось узнать побольше?"
    performances = [performance["performance_name"] for performance in
                    schedules]
    performances.append("Назад")

    return performances, text
