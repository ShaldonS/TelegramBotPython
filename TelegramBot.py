import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from yoomoney import Quickpay

# Токены и ключи
TOKEN = 'TOKEN'
YOOMONEY_TOKEN = 'YOOMONEY_TOKEN'
GOOGLE_SHEET_KEY = 'GOOGLE_SHEET_KEY'
GOOGLE_CREDENTIALS_JSON = 'google-credentials.json'


class TelegramBot:
    # Инициализация
    def __init__(self, token, yoomoney_token, google_sheet_key, google_credentials_json):
        self.bot = telebot.TeleBot(token)
        self.yoomoney_token = yoomoney_token
        self.google_sheet_key = google_sheet_key
        self.google_credentials_json = google_credentials_json
        self.dates_count = 0
        self.setup_google_sheets()
        self.setup_handlers()

    # Настройка Google Sheets
    def setup_google_sheets(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        # Авторизуем по json, скачаенному из service accounts
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.google_credentials_json, scope)
        gc = gspread.authorize(credentials)
        # Открываем лист по api ключу
        self.worksheet = gc.open_by_key(self.google_sheet_key).sheet1

    # Создание платежной ссылки
    def create_payment_link(self, amount):
        quickpay = Quickpay(
            receiver="410011161616877",
            quickpay_form="shop",
            targets="Оплата через Телеграм-бота",
            paymentType="SB",
            sum=amount,
            label="Оплата",
            comment="Тестовый платеж",
            successURL="https://ya.ru"
        )
        return quickpay.base_url

    # Проверка корректности даты
    def validate_date(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%d.%m.%Y')
            return True
        except ValueError:
            return False

    # Обработка нажатия кнопок
    def setup_handlers(self):
        # Обработчик команды /start
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            markup = self.create_keyboard()
            self.bot.send_message(message.chat.id, "Привет. Это бот с 4 кнопками", reply_markup=markup)

        # Обработчик кнопок
        @self.bot.message_handler(func=lambda message: True)
        def handle_text(message):
            if message.text == 'Яндекс карты':
                self.bot.send_message(message.chat.id, "Яндекс Карты: https://yandex.ru/maps/?text=Ленина%201")
            elif message.text == 'Оплата Yoomoney':
                payment_link = self.create_payment_link(2)
                self.bot.send_message(message.chat.id, f"Ссылка на оплату: {payment_link}", parse_mode='Markdown')
            elif message.text == 'Фото':
                photo = open('img1.jpg', 'rb')
                self.bot.send_photo(message.chat.id, photo)
            elif message.text == 'Значение А2':
                # Взятие значения ячейки
                value = self.worksheet.acell('A2').value
                self.bot.send_message(message.chat.id, f"Значение из ячейки A2: {value}")
            else:
                if self.validate_date(message.text):
                    # Установка значения ячейки
                    self.worksheet.update(f'B{self.dates_count}', message.text)
                    self.dates_count += 1
                    self.bot.reply_to(message, "Дата верна.")
                else:
                    self.bot.reply_to(message, "Дата неверна. Введите дату в формате ДД.ММ.ГГГГ")

    # Создание клавиатуры с кнопками
    def create_keyboard(self):
        markup = types.ReplyKeyboardMarkup(row_width=2)
        btn1 = types.KeyboardButton('Яндекс карты')
        btn2 = types.KeyboardButton('Оплата Yoomoney')
        btn3 = types.KeyboardButton('Фото')
        btn4 = types.KeyboardButton('Значение А2')
        markup.add(btn1, btn2, btn3, btn4)
        return markup

    # Запуск
    def run(self):
        self.bot.polling()

# Создание и запуск бота
if __name__ == '__main__':
    my_bot = TelegramBot(TOKEN, YOOMONEY_TOKEN, GOOGLE_SHEET_KEY, GOOGLE_CREDENTIALS_JSON)
    my_bot.run()