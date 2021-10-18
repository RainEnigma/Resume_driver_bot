import telebot
from telebot import types
from data import config


bot = telebot.TeleBot(config.API_TOKEN)


def applying_chosen_address(message, argum, arg_role):
    markup = types.InlineKeyboardMarkup(row_width=2)
    button_driver = types.InlineKeyboardButton(text="Да",
                                               callback_data=f"{argum}_{arg_role}_point_yes")
    button_passenger = types.InlineKeyboardButton(text="Нет",
                                                  callback_data=f"{argum}_{arg_role}_point_no")
    markup.add(button_driver, button_passenger)
    if argum == 'start':
        word = 'начальная'
    else:
        word = 'финальная'
    bot.send_message(message.chat.id,
                     f"это Ваша {word} точка?",
                     reply_markup=markup)
