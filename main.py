import telebot

if __name__ == '__main__':
    bot = telebot.TeleBot('1677667809:AAHH2KzZBHJl4NPS8Jqjrw4bMl6VYviQ8ac')


    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, f'Я бот. Приятно познакомиться, {message.from_user.first_name}')


    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        if message.text.lower() == 'привет':
            bot.send_message(message.from_user.id, 'Привет!')
        else:
            bot.send_message(message.from_user.id, 'Не понимаю, что это значит.')


    bot.polling(none_stop=True)