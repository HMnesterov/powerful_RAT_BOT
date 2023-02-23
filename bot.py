# bot
from collections import defaultdict

import telebot
from telebot import types
from settings import BOT_TOKEN

from random import sample
# libraries
import rotatescreen
import pathlib
from help_functions import get_files_and_dirs_in_directories

# some settings
bot = telebot.TeleBot(BOT_TOKEN)  # skip_pending=True)
file_location = pathlib.Path.cwd()
travel_path = pathlib.Path.cwd()

'''Words to protect callbacks from errors'''
from string import ascii_letters, digits

all_symbols = ascii_letters + digits
diction_with_code_words = {}
bd_for_callbacks = defaultdict(dict)


@bot.message_handler(commands=["start"])
def start(message, res=False):
    bot.send_message(message.chat.id, 'Init')


'''Screen tricks'''


@bot.message_handler(commands=['rotate_screen'])
def rotate_screen_main_function(message: str):
    """Keyboard for answers"""
    keyboard = types.InlineKeyboardMarkup()
    variants = (0, 90, 180, 270, 360)
    for variant in variants:
        keyboard_callback_button = types.InlineKeyboardButton(f'Rotate on {variant}',
                                                              callback_data=f"Degrees:{variant}")
        keyboard.add(keyboard_callback_button)
    bot.send_message(message.chat.id, text='Choose degrees', reply_markup=keyboard)


@bot.callback_query_handler(lambda call: call.data.startswith('Degrees:'))
def accept_rotate_screen_call(call):
    degrees_value = int(call.data.split(':')[1])
    screen = rotatescreen.get_primary_display()
    start_pos = screen.current_orientation
    pos = abs((start_pos - degrees_value) % 360)
    screen.rotate_to(pos)


# скрин с экрана


"""Directories travel functions"""


@bot.message_handler(commands=['travel_to_another_directory'])
def display_directories_to_go_in(message: str):
    global travel_path, diction_with_code_words, bd_for_callbacks

    code_word = ''.join(sample(all_symbols, 5))
    diction_with_code_words['directories_to_go_in'] = code_word

    directories = get_files_and_dirs_in_directories(travel_path).get('directories')
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    for indx, directory in enumerate(directories):
        # We need to destroy : symbols in 'directory'
        # We use index to contain directories paths in db because we cannot use so long path in callback_data
        directory = fr"{directory}"
        # Code word for callbacks
        bd_for_callbacks['travel_to_another_directory'][indx] = directory
        keyboard_callback_button = types.InlineKeyboardButton(fr'{directory}',
                                                              callback_data=fr"{code_word}{indx}", )
        keyboard.add(keyboard_callback_button)
    keyboard.add(types.InlineKeyboardButton('Back to previous directory', callback_data=f'{code_word}return_to_parent'))

    bot.send_message(message.chat.id, text='Make your choice', reply_markup=keyboard)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(f"{diction_with_code_words.get('directories_to_go_in')}"))
def go_to_directory(call):
    global travel_path, bd_for_callbacks
    indx = call.data[5:]

    if 'return_to_parent' in indx:
        travel_path = travel_path.parent
    else:
        indx = int(indx)
        path = bd_for_callbacks['travel_to_another_directory'][indx]

        last_elem = path
        travel_path = travel_path / last_elem.split('\\')[-1]
    display_directories_to_go_in(call.message)


# Запускаем бота
bot.polling(none_stop=True, interval=0)
