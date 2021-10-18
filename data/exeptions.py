import telebot
from data import config

bot = telebot.TeleBot(config.API_TOKEN)


class Something_with_poling(Exception):
    bot.send_message('238008205', "что-то произошло с попутчик-ботом")
