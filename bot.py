# bot
import shutil
from collections import defaultdict
import numpy
import telebot
from telebot import types
from settings import BOT_TOKEN

from random import sample
# libraries
import rotatescreen
import pathlib
from help_functions import get_files_and_dirs_in_directories, generate_code_word

# some settings
bot = telebot.TeleBot(BOT_TOKEN)  # skip_pending=True)
file_location = pathlib.Path.cwd()
travel_path = pathlib.Path.cwd()
diction_with_code_words = {}

bd_for_callbacks = defaultdict(dict)

data_for_files_operations = {}


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

    code_word = generate_code_word()
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
        travel_path = pathlib.Path(bd_for_callbacks['travel_to_another_directory'][indx])

    display_directories_to_go_in(call.message)


@bot.message_handler(commands=['see_all_files_in_travel_directory'])
def show_all_files_in_travel_directory(message: str):
    global travel_path, bd_for_callbacks, diction_with_code_words
    code_word = generate_code_word()
    diction_with_code_words['all_files'] = code_word
    data = get_files_and_dirs_in_directories(travel_path)
    files, dirs = data.get('files'), data.get('directories')

    keyboard = types.InlineKeyboardMarkup(row_width=1)

    for indx, directory in enumerate(files + dirs):
        directory = fr"{directory}"
        bd_for_callbacks['all_files'][indx] = directory
        keyboard_callback_button = types.InlineKeyboardButton(fr'{directory}',
                                                              callback_data=fr"{code_word}{indx}", )
        keyboard.add(keyboard_callback_button)

    bot.send_message(message.chat.id, text='Choose a file', reply_markup=keyboard)


@bot.callback_query_handler(
    lambda call: call.data.startswith(diction_with_code_words.get('all_files', 'ftsdgdsgsdgsd')))
def show_decisions_with_file(call: types.CallbackQuery):
    global travel_path, bd_for_callbacks, diction_with_code_words
    indx = int(call.data[5:])
    path = bd_for_callbacks['all_files'][indx]
    commands = ['delete', 'rename', 'copy']
    code_word = generate_code_word()
    diction_with_code_words['action_with_file'] = code_word
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    bd_for_callbacks['action_with_file']['path'] = path

    for value in commands:
        keyboard.add(types.InlineKeyboardButton(fr'{value}', callback_data=fr'{code_word}{value}'))
    keyboard.add(types.InlineKeyboardButton('Go back', callback_data='back'))
    bot.send_message(call.message.chat.id, text='What i need to do with this file?', reply_markup=keyboard)


@bot.callback_query_handler(lambda call: call.data == 'back')
def return_back_to_files_list(call):
    show_all_files_in_travel_directory(call.message)


@bot.callback_query_handler(lambda call:
                            call.data.startswith(diction_with_code_words.get('action_with_file', 'sefeswgewgew')) and
                            'delete' in call.data)
def remove_file(call: types.CallbackQuery):
    global bd_for_callbacks
    file_path = pathlib.Path(bd_for_callbacks['action_with_file']['path'])
    if file_path.is_dir():
        shutil.rmtree(file_path, ignore_errors=True)
    else:
        pathlib.Path.unlink(file_path)
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    bot.send_message(text=f'{file_path} was deleted!', chat_id=call.from_user.id, )


# Запускаем бота
bot.polling(none_stop=True, interval=0)
