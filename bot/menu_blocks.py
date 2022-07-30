from telegram import ReplyKeyboardMarkup
from more_itertools import chunked

from orm_commands import get_programs_list


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
    programs = get_programs_list()
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


def performance_block(performances_list, context,
                      user_is_back=False, user_choice=None):
    performances = []
    for perforamnce_id, performance in enumerate(performances_list,
                                                 start=1):
        performance_name = performance.name
        performance_time = performance.time
        performance = f'{perforamnce_id}. {performance_name}\n' \
                      f'Время: {performance_time}\n\n'
        performances.append(performance)

    if user_is_back:
        text = f"У программы «{context.user_data['performance']}» " \
               f"будут следующие выступления:\n\n" \
               f"{''.join(performances)}\n" \
               f"Про какое выступление вам бы хотелось узнать побольше?"
    else:
        text = f"У программы «{user_choice}» будут следующие выступления:\n\n" \
               f"{''.join(performances)}\n" \
               f"Про какое выступление вам бы хотелось узнать побольше?"

    performances = [performance.name for performance in
                    performances_list]
    performances.append("Назад")

    return performances, text
