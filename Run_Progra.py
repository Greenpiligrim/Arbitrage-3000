from Run_First_JSON import process_first_json
from Run_Second_JSON import process_second_json
from Get_Crypto_Price import get_crypto_price

def run_program(selected_crypto, selected_currency, my_limit, transfer_fee, selected_exchange, selected_transfer_exchange, price_difference_percentage_1, price_difference_percentage_2):
    # Печатаем все входящие параметры для отладки
    # print("selected_crypto:", selected_crypto)
    # print("selected_currency:", selected_currency)
    # print("my_limit:", my_limit)
    # print("transfer_fee:", transfer_fee)
    # print("selected_exchange:", selected_exchange)
    # print("selected_transfer_exchange:", selected_transfer_exchange)
    # print("price_difference_percentage_1:", price_difference_percentage_1)
    # print("price_difference_percentage_2:", price_difference_percentage_2)
    # print("____________________________________")

    # Создаем словари для сопоставления выбранных значений с соответствующими частями trade_class
    currency_mapping = {"RUB": "rub", "USD": "usd"}
    crypto_mapping = {"USDT": "usdt", "BTC": "btc", "ETH": "eth"}

    # Формируем части trade_class из выбранных значений
    crypto_part = crypto_mapping.get(selected_crypto)
    currency_part = currency_mapping.get(selected_currency)

    # Формируем полный trade_class
    trade_class = f"sell-{crypto_part}-{currency_part}"

    # Получаем текущий курс с CoinGeco.com
    price, pair = get_crypto_price(trade_class)

    
    # Выбираем правильные ссылки в зависимости от выбранной биржи для блока "На бирже"
    # if selected_exchange == "ByBit":
    #     json_link_exchange = "r_byBit.json"
    # else:
    #     json_link_exchange = "r_htx.json"

    if selected_exchange == "ByBit":
        json_link_exchange = "sellers_info_bybit.json"
    else:
        json_link_exchange = "sellers_info_htx.json"

    # Выбираем правильные ссылки в зависимости от выбранной биржи для блока "Перевожу на биржу"
    # if selected_transfer_exchange == "ByBit":
    #     json_link_transfer = "r_byBit.json"
    # else:
    #     json_link_transfer = "r_htx.json"

    if selected_transfer_exchange == "ByBit":
        json_link_transfer = "sellers_info_bybit.json"
    else:
        json_link_transfer = "sellers_info_htx.json"

    # Для process_first_json
    trade_class_1 = "sell"
    # Формируем полный trade_class для process_first_json
    me_trade_class_1 = f"{trade_class_1}-{crypto_part}-{currency_part}"

    # Для process_second_json
    trade_class_2 = "buy"
    me_trade_class_2 = f"{trade_class_2}-{crypto_part}-{currency_part}"

    # print("crypto_part:", crypto_part)
    # print("currency_part:", currency_part)
    # print("price:", price)
    # print("pair:", pair)
    # print("json_link_exchange:", json_link_exchange)
    # print("json_link_transfer:", json_link_transfer)
    # print("me_trade_class_1:", me_trade_class_1)
    # print("me_trade_class_2:", me_trade_class_2)
    # print("____________________________________")

    # Обработка первого JSON
    result_first_json = process_first_json(json_link_exchange, me_trade_class_1, my_limit, price, pair, price_difference_percentage_1)
    amount, operation_description = result_first_json

    # Обработка второго JSON
    operation_text = process_second_json(amount, transfer_fee, my_limit, me_trade_class_2, json_link_transfer, price_difference_percentage_2)
    return operation_description, operation_text
