#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job
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
HELP_CMDS = config.get('commands', 'help').replace(" ", "").split(',')
TODAY_CMDS = config.get('commands', 'today').replace(" ", "").split(',')
FUTURE_CMDS = config.get('commands', 'future').replace(" ", "").split(',')
SUB_CMDS = config.get('commands', 'subscribe').replace(" ", "").split(',')
UNSUB_CMDS = config.get('commands', 'unsubscribe').replace(" ", "").split(',')


SUB_FREQUENCY = float(config.get('subscribe', 'frequency'))

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

def escape_md(msg):
    return msg.replace("_","\_")

def processEvent(event, condition):
    name = event['name']
    location = event['location_name']
    starts_at = event['starts_at']
    starts_at_t = getEventTime(starts_at)
    if condition(starts_at_t):
        return escape_md("*" + name + "* @ " + \
            readableTime(starts_at) + " - " + location + "\n\n")

    return ''


def start_handle(bot, update):
    """Return a welcome message to the user"""
    msg = config.get('messages', 'welcome')
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg.format(
                         user_name=update.message.from_user.first_name,
                         bot_name=bot.name,
                         help_cmd=HELP_CMDS))


def help_handle(bot, update):
    """Return a list of instruction on how to use the bot"""
    msg = config.get('messages', 'help')
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg.format(
                         today_cmd=TODAY_CMDS,
                         future_cmd=FUTURE_CMDS,
                         sub_cmd=SUB_CMDS,
                         unsub_cmd=UNSUB_CMDS))


def today_handle(bot, update):
    """Return list of events happening today"""
    events = getEvents()

    today_events = ''
    for event in events:
        today_events += processEvent(event, isToday)

    if not today_events:
        event_string = processEvent(events[0],isFuture)
        msg = config.get('messages', 'failure') + "\n\n" + \
                config.get('messages', 'next_event') + "\n" + \
                event_string.encode('utf8')
        bot.sendMessage(chat_id=update.message.chat_id, text=msg, 
            parse_mode=telegram.ParseMode.MARKDOWN)
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


def get_job(jobs, chat_id):
    for job in jobs:
        if job.is_enabled() and job.context.message.chat_id == chat_id:
            return job

    return None


def sub_job_handle(bot, job):
    subscribe_header_msg=config.get('messages', 'subscribe_header').format(user_name=job.context.message.from_user.first_name, unsub_cmd=UNSUB_CMDS)
    bot.send_message(chat_id=job.context.message.chat_id, text=subscribe_header_msg)
    today_handle(bot, job.context)


def sub_handle(bot, update, job_queue):
    chat_id = update.message.chat_id
    job = get_job(job_queue.jobs(), chat_id)
    if job is None:
        msg = config.get('messages', 'subscribe')
        hours = int(SUB_FREQUENCY/3600)
        bot.send_message(chat_id=chat_id, text=msg.format(frequency=hours))

        job = Job(sub_job_handle, SUB_FREQUENCY, repeat=True, context=update)
        job_queue.put(job, next_t=0.0)
    else:
        msg = config.get('messages', 'subscribe_fail')
        bot.send_message(chat_id=chat_id, text=msg)


def unsub_handle(bot, update, job_queue):
    chat_id = update.message.chat_id
    job = get_job(job_queue.jobs(), chat_id)
    if job is None:
        msg = config.get('messages', 'unsubscribe_fail')
        bot.sendMessage(chat_id=chat_id, text=msg)
    else:
        msg = config.get('messages', 'unsubscribe')
        bot.sendMessage(chat_id=chat_id, text=msg)
        job.set_enabled(False)
        job.schedule_removal()
        


def error_handle(bot, update, error):
    """Handle errors"""
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    logger.info('Starting the Unni Bot!')
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler(START_CMD, start_handle))

    for help_cmd in HELP_CMDS:
        dp.add_handler(CommandHandler(help_cmd, help_handle))

    for today_cmd in TODAY_CMDS:
        dp.add_handler(CommandHandler(today_cmd, today_handle))

    for future_cmd in FUTURE_CMDS:
        dp.add_handler(CommandHandler(future_cmd, future_handle))

    for sub_cmd in SUB_CMDS:
        dp.add_handler(CommandHandler(sub_cmd, sub_handle, pass_job_queue=True))
    
    for unsub_cmd in UNSUB_CMDS:
        dp.add_handler(CommandHandler(unsub_cmd, unsub_handle, pass_job_queue=True))

    dp.add_error_handler(error_handle)

    updater.start_polling()
    logger.info('Unni Bot started!')
    updater.idle()

if __name__ == '__main__':
    main()
