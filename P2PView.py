# _____работает!!!______

#Это вью с автоматическим переставлением валют

import wx
from Run_Progra import run_program

class MyFrameTest(wx.Panel):  # Изменяем наследование на wx.Panel
    def __init__(self, parent=None, title="АРБИТРАЖ - 3000"):
        super().__init__(parent=parent)
        vbox = wx.BoxSizer(wx.VERTICAL)

        fields = [
            ("Я покупаю криптовалюту:", ["USDT", "BTC", "ETH"]),
            ("На бирже:", ["Huobi", "ByBit"]),
            ("Покупаю за:", ["RUB", "USD"]),
            ("На сумму:", None),
            ("Покупаю дешевле рыночного курса на (%):", None),
            ("Перевожу на биржу:", ["ByBit", "Huobi"]),
            ("Комиссия перевода:", None),
            ("Я продаю криптовалюту:", ["USDT", "BTC", "ETH"]),
            ("Продаю за:", ["RUB", "USD"]),
            ("Продаю дороже рыночного курса на (%):", None)
        ]

        self.controls = {}  # Словарь для хранения ссылок на элементы управления
        for label_text, choices in fields:
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self, label=label_text)
            hbox.Add(label, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10)

            if choices:
                control = wx.Choice(self, choices=choices)
                if label_text in ["Я покупаю криптовалюту:", "Я продаю криптовалюту:"]:
                    control.Bind(wx.EVT_CHOICE, self.on_crypto_choice)  # Привязываем обработчик для выбора криптовалюты
                elif label_text == "Покупаю за:" or label_text == "Продаю за:":
                    control.Bind(wx.EVT_CHOICE, self.on_currency_choice)  # Привязываем обработчик для выбора валюты
            else:
                control = wx.TextCtrl(self)
            hbox.Add(control, proportion=1)
            vbox.Add(hbox, flag=wx.EXPAND | wx.ALL, border=10)

            # Сохраняем ссылки на элементы управления
            self.controls[label_text] = control

        # Создание кнопок и текстового поля для вывода результатов
        self.create_widgets(vbox)

        self.SetSizer(vbox)

    def create_widgets(self, vbox):
        # Создание кнопки "Рассчитать"
        self.run_button = wx.Button(self, label="Анализ рынка")
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run)
        vbox.Add(self.run_button, flag=wx.EXPAND | wx.ALL, border=10)

        # Создание текстового поля для вывода результатов
        self.console_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        font1 = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial")
        self.console_text.SetFont(font1)
        self.console_text.SetForegroundColour(wx.Colour(255, 255, 255))
        self.console_text.SetBackgroundColour(wx.Colour(23, 38, 55))
        vbox.Add(self.console_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

    def on_crypto_choice(self, event):
        selected_crypto = event.GetString()
        for label_text, control in self.controls.items():
            if label_text in ["Я покупаю криптовалюту:", "Я продаю криптовалюту:"] and control != event.GetEventObject():
                control.SetSelection(control.FindString(selected_crypto))

    def on_currency_choice(self, event):
        selected_currency = event.GetString()
        for label_text, control in self.controls.items():
            if label_text in ["Покупаю за:", "Продаю за:"] and control != event.GetEventObject():
                control.SetSelection(control.FindString(selected_currency))

    def on_run(self, event):
        # Получаем значения из полей ввода
        try:
            my_limit = int(self.controls["На сумму:"].GetValue())
            transfer_fee = float(self.controls["Комиссия перевода:"].GetValue())
            selected_crypto = self.controls["Я покупаю криптовалюту:"].GetStringSelection()
            selected_currency = self.controls["Покупаю за:"].GetStringSelection()
            selected_exchange = self.controls["На бирже:"].GetStringSelection()
            selected_transfer_exchange = self.controls["Перевожу на биржу:"].GetStringSelection()
            price_difference_percentage_1 = int(self.controls["Покупаю дешевле рыночного курса на (%):"].GetValue())
            price_difference_percentage_2 = int(self.controls["Продаю дороже рыночного курса на (%):"].GetValue())

            # Проверка на пустые поля
            if not my_limit or not transfer_fee:
                wx.MessageBox("Пожалуйста, заполните все поля.", "Ошибка")
                return

        except ValueError:
            wx.MessageBox("Пожалуйста, введите числовые значения для лимита и комиссии.", "Ошибка")
            return
        
        # Выполняем обработку данных
        operation_description, operation_text = run_program(selected_crypto, selected_currency, my_limit, transfer_fee, selected_exchange, selected_transfer_exchange,price_difference_percentage_1, price_difference_percentage_2)

        # Очищаем текстовое поле
        self.console_text.Clear()

        # Объединяем оба текста
        combined_text = operation_description + "\n\n" + operation_text

        # Выводим информацию в текстовое поле
        self.console_text.SetValue(combined_text)

    def on_exit(self, event):
        self.Close()
