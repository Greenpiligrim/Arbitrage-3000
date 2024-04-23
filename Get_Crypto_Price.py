import requests

def get_crypto_price(trade_class):
    """
    Получение курса с Coin Geco 

    Использование: 

    from Get_Crypto_Price import get_crypto_price
    b = "sell-eth-usd"
    price, pair = get_crypto_price(b)
    print(f"Актуальный курс {pair}: {price}")

        
    """
    # Разбиваем строку "trade_class" по разделителю "-"
    parts = trade_class.split("-")
    
    # Проверяем, что строка имеет правильный формат
    if len(parts) != 3:
        print("Ошибка: неверный формат строки 'trade_class'")
        return None
    
    # Создаем словарь для преобразования сокращенных названий криптовалют в полные названия
    crypto_converter = {
        'btc': 'bitcoin',
        'eth': 'ethereum',
        'usdt': 'tether'
    }
    
    # Извлекаем название криптовалюты и валюту
    cryptocurrency = crypto_converter.get(parts[1])
    currency = parts[2]
    
    # Проверяем, была ли найдена полная форма названия криптовалюты
    if cryptocurrency is None:
        print(f"Ошибка: неверное сокращение криптовалюты '{parts[1]}'")
        return None
    
    # Формируем URL для запроса к CoinGecko API
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={cryptocurrency}&vs_currencies={currency}"
    
    try:
        # Отправляем GET-запрос к API
        response = requests.get(url)
        
        # Проверяем статус код ответа
        if response.status_code == 200:
            # Получаем данные в формате JSON
            data = response.json()
            
            # Извлекаем цену криптовалюты в указанной валюте
            crypto_price = data[cryptocurrency][currency]
            
            # Формируем обозначение пары криптовалюты
            pair = f"{parts[1].upper()}-{parts[2].upper()}"
            
            return crypto_price, pair
        else:
            # Если запрос не удался, выводим сообщение об ошибке
            print("Ошибка при получении данных. Статус код:", response.status_code)
            return None
    except Exception as e:
        # Если произошла какая-то ошибка при выполнении запроса, выводим сообщение об ошибке
        print("Произошла ошибка:", str(e))
        return None
