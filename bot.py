# bot
import shutil

import numpy
import telebot
from telebot import types
from settings import BOT_TOKEN

# libraries
import rotatescreen
import pathlib
from help_functions import get_files_and_dirs_in_directories

# some settings
bot = telebot.TeleBot(BOT_TOKEN, skip_pending=True)
file_location = pathlib.Path.cwd()
travel_path = pathlib.Path.cwd()


@bot.message_handler(commands=["start"])
def start(message, res=False):
    bot.send_message(message.chat.id, 'Init')


'''Screen tricks'''


@bot.message_handler(commands=['rotate_screen'])
def rotate_screen_main_function(message):
    msg = bot.send_message(message.chat.id, "Input degrees count: 0, 90, 180, 270")
    bot.register_next_step_handler(msg, make_rotate)


def make_rotate(message):
    if message.text == 'out':
        bot.send_message(message.chat.id, "Command is closed..")
        return
    try:
        degrees = int(message.text)
        screen = rotatescreen.get_primary_display()
        start_pos = screen.current_orientation
        pos = abs((start_pos - degrees) % 360)
        screen.rotate_to(pos)
        msg = "Successfully"
    except:
        msg = "You can use only 0, 90, 180, 270 degrees!"
    bot.send_message(message.chat.id, msg)


"""Directories travel functions"""


@bot.message_handler(commands=['cd'])
def display_directories_to_go_in(message):
   # print(message.text)
    global travel_path
    directories = get_files_and_dirs_in_directories(travel_path).get('directories')
    bot.send_message(message.chat.id,
                     "Choice path to go and enter it's index(leave from command - 'out', 'parent' - step back")
    text = """"""
    for indx, value in enumerate(directories):
        text += f'{indx} - {value}\n'
    if not text:
        text = """There is no other directories, you can only back to parent!"""
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, cd_to_directory, directories)


def cd_to_directory(message, directories):
   # print(message.text)
    global travel_path
    path = message.text
    if path == 'out':
        bot.send_message(message.chat.id, 'Command is closed')
        return

    if path == 'parent':
        travel_path = travel_path.parent
        bot.send_message(message.chat.id, f'You are here\n{travel_path}')
    else:
        try:
            travel_path = directories[int(path)]
            bot.send_message(message.chat.id, f'You are here\n{travel_path}')
        except:
            bot.send_message(message.chat.id, 'Unknown path')

    display_directories_to_go_in(message)


#
# @bot.message_handler()
# def go_to_directory(message: str):
#    global travel_path
#
#    travel_path = travel_path.parent
#
#    travel_path = pathlib.Path(...)
#
#    display_directories_to_go_in(message)
#
#
# @bot.message_handler(commands=['see_all_files_in_travel_directory'])
# def show_all_files_in_travel_directory(message: str):
#    global travel_path
#    data = get_files_and_dirs_in_directories(travel_path)
#    files, dirs = data.get('files'), data.get('directories')
#
#
# @bot.message_handler()
# def remove_file(message: str):
#    file_path = ...
#    if file_path.is_dir():
#        shutil.rmtree(file_path, ignore_errors=True)
#    else:
#        pathlib.Path.unlink(file_path)


# Запускаем бота
bot.polling(none_stop=True, interval=0)
