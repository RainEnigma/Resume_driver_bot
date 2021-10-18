from telebot import types


def admin_conf(bot, message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button_statistics = types.KeyboardButton("колличество людей")
    button_clear_scr = types.KeyboardButton("очистить экран")
    markup.add(button_statistics, button_clear_scr)

    bot.send_message(message.chat.id,
                     "🧞‍♂ Привет!",
                     reply_markup=markup)
    markup1 = types.InlineKeyboardMarkup(row_width=2)

    button_driver = types.InlineKeyboardButton(text="🚙 Водитель",
                                               callback_data="Водитель")
    button_passenger = types.InlineKeyboardButton(text="🚶‍♂ Пассажир",
                                                  callback_data="Пассажир")

    markup1.row(button_driver, button_passenger)
    bot.send_message(message.chat.id,
                     f"🧞‍♂ чего желаете?",
                     reply_markup=markup1)
