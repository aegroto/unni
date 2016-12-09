#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import os
import urllib2
import json
from datetime import datetime

CONFIG_FILE = 'unni.cfg'
config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)

# Enable logging
LOG_DIR = config.get('log', 'dir')
LOG_FILE = config.get('log', 'name')
TELEGRAM_TOKEN = config.get('telegram', 'token')
SOURCE_NAME = config.get('source', 'name')
SOURCE_URL = config.get('source', 'url')

# Top level commands for the bot
START_CMD = 'start'
HELP_CMD = 'help'
TODAY_CMD = 'today'
FUTURE_CMD = 'future'

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
logging.basicConfig(filename=LOG_DIR + "/" + LOG_FILE,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger()
logger.info('Logger initialised')


def getEventTime(time):
    #time = time[0:10] + ' ' + time[11:19]
    time = time[0:23]
    time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f')
    return time


def readableTime(time):
    time = time[0:10] + ' ' + time[11:16]
    return unicode(datetime.strptime(time, '%Y-%m-%d %H:%M'))[:-3]


def isToday(time):
    return time.date() == datetime.today().date()


def isFuture(time):
    return time.date() > datetime.today().date()


def start_handle(bot, update):
    """Return a welcome message to the user"""
    msg = "Hello {user_name}! I am {bot_name} \n"
    msg += "Type /help for any info on how to interact with me"

    # Send the message
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg.format(
                         user_name=update.message.from_user.first_name,
                         bot_name=bot.name))


def help_handle(bot, update):
    """Return a list of instruction on how to use the bot"""
    help = 'Hello! I am unni_bot :) \n\n'\
        'The available commands are: \n'\
        '- /today \n'\
        '- /future'

    bot.sendMessage(update.message.chat_id, text=help)


def today_handle(bot, update):
    """Return list of events happening today"""
    msg = 'The events of today are: \n'
    for event in events:
        name = event['name']
        starts_at = event['starts_at']
        starts_at_t = getEventTime(starts_at)
        if isToday(starts_at_t):
            msg += "*" + name + "* @ " + readableTime(starts_at) + "\n"

    bot.sendMessage(update.message.chat_id, text=msg,
                    parse_mode=telegram.ParseMode.MARKDOWN)


def future_handle(bot, update):
    """Return list of future events"""
    response = urllib2.urlopen(SOURCE_URL)
    events = json.load(response)

    msg = 'The upcoming events are: \n'
    for event in events:
        name = event['name']
        starts_at = event['starts_at']
        starts_at_t = getEventTime(starts_at)
        if isFuture(starts_at_t):
            msg += "*" + name + "* @ " + readableTime(starts_at) + "\n"

    bot.sendMessage(update.message.chat_id, text=msg,
                    parse_mode=telegram.ParseMode.MARKDOWN)


def error_handle(bot, update, error):
    """Handle errors"""
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    logger.info('Starting Bot!')
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler(START_CMD, start_handle))
    dp.add_handler(CommandHandler(HELP_CMD, help_handle))
    dp.add_handler(CommandHandler(TODAY_CMD, today_handle))
    dp.add_handler(CommandHandler(FUTURE_CMD, future_handle))

    dp.add_error_handler(error_handle)

    updater.start_polling()
    logger.info('Unni Bot started!')

    updater.idle()

if __name__ == '__main__':
    main()
