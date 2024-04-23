import os
import json

def process_second_json(amount, transfer_fee, my_limit, trade_class_2, json_link_2, price_difference_percentage):
    """
    Обработка второго JSON.

    Args:
    amount (float): Количество валюты.
    transfer_fee (float): Комиссия перевода на другую биржу.
    my_limit (float): Указанный лимит.
    price (float): Рыночный курс.
    trade_class_2 (str): Класс торгов для второго JSON.
    json_link_2 (str): Ссылка на второй JSON файл.
    price_difference_percentage (float): Процент разницы от рыночной цены для фильтрации продавцов. (по умолчанию 10)
    
    Returns:
    str: Текстовое описание операции.
    """
    # Преобразуем my_limit в float, если он не является числом
    try:
        my_limit = float(my_limit)
    except ValueError:
        return "Ошибка: Указанный лимит не является числом."

    # Получаем текущую директорию
    current_directory = os.getcwd()

    # Формируем путь к файлу sellers_info_bybit.json
    file_path_2 = os.path.join(current_directory, json_link_2)

    # Проверяем существует ли файл
    if os.path.exists(file_path_2):
        # Открываем файл на чтение
        with open(file_path_2, 'r') as file_2:
            # Загружаем данные из файла JSON
            data_2 = json.load(file_2)

        # Фильтруем данные по trade_class_2
        filtered_data_by_class = [entry for entry in data_2 if entry.get("trade_class") == trade_class_2]

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
        my_price = market_rate + price_difference

        # Фильтруем данные по максимальной близости к price_plus_price
        filtered_data_2 = [entry for entry in filtered_data_by_limit if market_rate <= float(entry.get("price")) < my_price]


        # Если есть подходящие данные, продолжаем обработку
        if filtered_data_2:
            # Сортируем отфильтрованные данные по цене по убыванию
            sorted_data_2 = sorted(filtered_data_2, key=lambda x: float(x["price"]))

            # Находим количество экземпляров в верхней половине списка
            half_index = len(filtered_data_2) // 2

            # Берем верхнюю половину экземпляров
            top_half = filtered_data_2[half_index:]

            # Находим среднюю цену в верхней половине экземпляров
            average_price = round(sum(float(item.get("price")) for item in top_half) / len(top_half), 2)

            # Получаем первых пять продавцов с наибольшей ценой
            top_sellers_data_2 = top_half[:5]

            # Получаем цену первого экземпляра с учетом указанного процента разницы от рыночного курса
            first_price_2 = float(top_sellers_data_2[0]["price"])

            # Получаем название биржи из первого продавца
            exchange_name_2 = top_sellers_data_2[0].get("market", "неизвестно")

            # Определяем звание коина
            currency_2 = trade_class_2.split("-")[1].upper()

            # Определяем тип операции (покупка/продажа) и валюту
            operation_2 = "продаете" if "buy" in trade_class_2 else "покупаете"

            # Определяем валюту обмена
            exchange_currency = trade_class_2.split("-")[-1].upper()

            # Рассчитываем сумму с учетом комиссии
            y = amount - transfer_fee
            z = y * first_price_2
            profit = round(z - my_limit, 2)
            spread_percentage = round((profit / my_limit) * 100, 2)

            # Формируем предложения

            operation_description = f"Минус комиссия: {transfer_fee} {currency_2} за превод.\n"
            operation_description += f"У вас теперь: {y} {currency_2}\n"
            operation_description += f"-----------------------------------------------------------------------\n"
            operation_description += f"РЕКОМЕНДАЦИИ для биржи: {exchange_name_2}:\n"
            operation_description += f" - Продайте {y} {currency_2} по по средне-биржевому курсу: {first_price_2} {exchange_currency}\n"
            operation_description += f" - Прибыль составит: {profit} {exchange_currency}\n"                        
            operation_description += f" - Спред: {spread_percentage} %\n"
            operation_description += f"-----------------------------------------------------------------------\n"
            operation_description += f"*** Вы продали на {price_difference_percentage} % выше рыночной цены\n"
            operation_description += f"-----------------------------------------------------------------------\n"
            # Возвращаем текстовое описание операции
            return operation_description
        else:
            return "Подходящих рекомендаций по связке не обнаружено! Попробуйте изменить процент от рыночной цены покупка/продажа"
    else:
        return "Файл 'sellers_info_bybit.json' не существует."

# Пример использования функции
# operation_text = process_second_json(100, 2, 50, 120, "BTC-USDT", "data.json")
# print(operation_text)
