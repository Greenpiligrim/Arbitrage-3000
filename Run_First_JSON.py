import os
import json
#def process_first_json(json_link, trade_class, my_limit, price, pair, price_difference_percentage):

def process_first_json(json_link, trade_class, my_limit, price, pair, price_difference_percentage):
    """
    Обработка первого JSON.

    Args:
    json_link (str): Ссылка на JSON файл.
    trade_class (str): Класс торгов.
    my_limit (float): Указанный лимит.
    price (float): Рыночная цена.
    pair (str): Пара криптовалют.
    price_difference_percentage (float): Процент разницы от рыночной цены для фильтрации продавцов.

    Returns:
    tuple: Кортеж, содержащий количество валюты (amount) и текстовое описание операции (operation_description).
    """

    # Получаем текущую директорию
    current_directory = os.getcwd()

    # Формируем путь к файлу sellers_info_htx.json
    file_path = os.path.join(current_directory, json_link)

    # Проверяем существует ли файл
    if os.path.exists(file_path):
        # Открываем файл на чтение
        with open(file_path, 'r') as file:
        # Загружаем данные из файла JSON
            data = json.load(file)

        # Фильтруем данные по trade_class
        filtered_data_by_class = [entry for entry in data if entry.get("trade_class") == trade_class]

        # Фильтруем данные по указанному лимиту с условием, что лимит должен быть выше чем 75% от my_limit
        filtered_data_by_limit = [entry for entry in filtered_data_by_class if float(entry.get("limit", 0)) > my_limit * 0.75]

        #Извлекаем Сигнатуру
        # Получаем первый экземпляр из списка
        first_instance = filtered_data_by_limit[0]
        # Извлечение значения "market rate"
        market_rate = float(first_instance.get("market_rate", 0))  # По умолчанию 0, если значение отсутствует или не может быть преобразовано в число
        # Извлечение значения "data" в виде строки
        data_str = first_instance.get("data", "")
        

        # Вычисляем разницу в процентах от рыночной цены
        price_difference = market_rate * price_difference_percentage / 100
        my_price = market_rate - price_difference #дешевле на указанный процент

        # Фильтруем данные по максимальной близости к my_price
        filtered_data_2 = sorted(filtered_data_by_limit, key=lambda x: abs(float(x.get("price")) - my_price), reverse=True)


        # Находим количество экземпляров в верхней половине списка
        half_index = len(filtered_data_2) // 2

        # Берем верхнюю половину экземпляров
        top_half = filtered_data_2[half_index:]

        # Находим среднюю цену в верхней половине экземпляров
        average_price = round(sum(float(item.get("price")) for item in top_half) / len(top_half), 2)

        # Определяем тип операции (покупка/продажа) и валюту
        currency = ""
        if "-eth-" in trade_class:
            currency = "ETH"
        elif "-btc-" in trade_class:
            currency = "BTC"
        elif "-usdt-" in trade_class:
            currency = "USDT"

        # Определяем валюту обмена
        exchange_currency = trade_class.split("-")[-1].upper()

        # Получаем название биржи из поля "market"
        exchange_name = first_instance.get("market", "неизвестно")

        # Рассчитываем количество валюты, которую получите за указанный лимит
        amount = my_limit / average_price

        # Формируем текстовое описание операции
        operation_description =  f"Актуальный рыночный курс : {pair} {price}\n"
        operation_description += f"-----------------------------------------------------------------------\n"
        operation_description += f"Расчетный   рыночный курс : {pair} {market_rate}  (курс на момент обработки данных {data_str})\n"
        operation_description += f"-----------------------------------------------------------------------\n"
        operation_description += f"РЕКОМЕНДАЦИИ для биржи {exchange_name}:\n"
        operation_description += f" - Покупайте на {my_limit} {exchange_currency} по средне-биржевому курсу: {average_price} {exchange_currency}\n"
        operation_description += f" - У вас теперь: {amount} {currency}\n"

        operation_description += f"-----------------------------------------------------------------------\n"
        operation_description += f"*** Вы купили на {price_difference_percentage} % ниже рыночной цены\n"
        operation_description += f"-----------------------------------------------------------------------\n"

        # Возвращаем кортеж с количеством валюты и текстовым описанием операции
        return amount, operation_description
    else:
        print("File 'sellers_info_bybit.json' does not exist.")
