#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import os

# Enable logging
LOGS_DIR = 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
logging.basicConfig(filename=LOGS_DIR + '/bot.log',
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.INFO)

logger = logging.getLogger(__name__)

# loading token from config file
logger.info('Loading token from file')
tokenconf = open('token.conf', 'r').read()
TOKEN = tokenconf

def start_handle(bot, update):
	"""Return a welcome message to the user"""
	bot.sendMessage(update.message.chat_id, text=
		"Hello and Welcome to the sciabaca's bot!\n" \
		"Type /help for any info on how to interact with me")

def help_handle(bot, update):
	"""Return a list of instruction on how to use the bot"""
	help = 'Hello! I am unni_bot :) \n\n'\
			'The available commands are: \n'

	bot.sendMessage(update.message.chat_id, text=help)

def today_handle(bot, update):
	"""Return list of events happening today"""
	print 'Not Implemented'

def future_handle(bot, update):
	"""Return list of future events"""
	print 'Not Implemented'

def error_handle(bot, update, error):
	"""Handle errors"""
	logger.warn('Update "%s" caused error "%s"' % (update, error))

# Top level commands for the bot
START_CMD = 'start'
HELP_CMD = 'help'
TODAY_CMD = 'today'
FUTURE_CMD = 'future'

def main():
	logger.info('Starting Bot!')
	updater = Updater(TOKEN)

	dp = updater.dispatcher

	dp.add_handler(CommandHandler(START_CMD, start_handle))
	dp.add_handler(CommandHandler(HELP_CMD, help_handle))
	dp.add_handler(CommandHandler(TODAY_CMD, today_handle))
	dp.add_handler(CommandHandler(FUTURE_CMD, future_handle))

	dp.add_error_handler(error_handle)

	updater.start_polling()
	logger.info('Bot started!')

	updater.idle()

if __name__ == '__main__':
	main()
