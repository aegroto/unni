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
START_CMD = config.get('commands', 'start')
HELP_CMD = config.get('commands', 'help')
TODAY_CMD = config.get('commands', 'today')
FUTURE_CMD = config.get('commands', 'future')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
logging.basicConfig(filename=LOG_DIR + "/" + LOG_FILE,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger()
logger.info('Logger initialised')


def getEventTime(time):
    time = time[0:23]
    time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f')
    return time


def readableTime(time):
    time = time[0:10]
    return unicode(datetime.strptime(time, '%Y-%m-%d'))[:-8]


def isToday(time):
    return time.date() == datetime.today().date()


def isFuture(time):
    return time.date() > datetime.today().date()


def getEvents():
    response = urllib2.urlopen(SOURCE_URL)
    return json.load(response)


def processEvent(event, condition):
    name = event['name']
    location = event['location_name']
    starts_at = event['starts_at']
    starts_at_t = getEventTime(starts_at)
    if condition(starts_at_t):
        return "*" + name + "* @ " + \
            readableTime(starts_at) + " - " + location + "\n\n"

    return ''


def start_handle(bot, update):
    """Return a welcome message to the user"""
    msg = config.get('messages', 'welcome')
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg.format(
                         user_name=update.message.from_user.first_name,
                         bot_name=bot.name,
                         help_cmd=HELP_CMD))


def help_handle(bot, update):
    """Return a list of instruction on how to use the bot"""
    msg = config.get('messages', 'help')
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg.format(
                         today_cmd=TODAY_CMD,
                         future_cmd=FUTURE_CMD))


def today_handle(bot, update):
    """Return list of events happening today"""
    events = getEvents()

    today_events = ''
    for event in events:
        today_events += processEvent(event, isToday)

    if not today_events:
        msg = config.get('messages', 'failure')
        bot.sendMessage(chat_id=update.message.chat_id, text=msg)
    else:
        msg = config.get('messages', 'today')
        msg += "\n" + today_events
        bot.sendMessage(chat_id=update.message.chat_id, text=msg,
                        parse_mode=telegram.ParseMode.MARKDOWN)


def future_handle(bot, update):
    """Return list of future events"""
    events = getEvents()

    future_events = ''
    for event in events:
        future_events += processEvent(event, isFuture)

    if not future_events:
        msg = config.get('messages', 'failure')
        bot.sendMessage(update.message.chat_id, text=msg)
    else:
        msg = config.get('messages', 'future')
        msg += "\n" + future_events
        bot.send_message(chat_id=update.message.chat_id, text=msg,
                         parse_mode=telegram.ParseMode.MARKDOWN)


def error_handle(bot, update, error):
    """Handle errors"""
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    logger.info('Starting the Unni Bot!')
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
