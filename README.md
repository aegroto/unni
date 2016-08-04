# unni
unni is a Telegram Bot that gives info about events from sciabaca

**unni** is the Sicilian word for *where*. That is one of the main questions people ask about events: where is it? **unni**, however, provides more information about events than just where that happen. 

**unni** will serve the events data from [**sciabaca**](https://github.com/sic2/sciabaca). 

## commands

This is the list of commands supported by **unni**

- /help
- /today
- /future

We would love to have other commands, such as `/topic` or `/city`, in the future. 

## Running the Bot Locally

This bot is using the [python-telegram-bot library](https://github.com/python-telegram-bot/python-telegram-bot).

The first step to run the bot is to install the required dependencies. You can do this via **pip**

```
$ pip install python-telegram-bot --upgrade
```

Then call the [@BotFather](https://telegram.me/BotFather) within Telegram and use the `/newbot` command to create a new bot. Then do the following:

```
$ touch token.conf # this will create an empty file named token.conf

# Open token.conf using your favourite editor
# Paste the bot's token in the first line of the configuration file
# Add an empty line at the end of the file
```

Then run:

```
$ python unni.py
```

Now you can call your bot on telegram and have fun! 


## Testing the deployed Bot

You can test it by adding the [unni_bot](http://telegram.me/unni_bot) to your Telegram

## Info

This project is currently maintained by the [PAC Community](https://www.facebook.com/groups/programmatoriCatania/) and it is under the MIT license. Feel free to use and modify it.
