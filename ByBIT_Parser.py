#__________не______трогать__________работает!!!______
#Закрывает банер переключает страницы переходит по другим ссылкам
#Если нужно увеличь слип чтобы успевало парситься
import datetime
import time
import re
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup 
from Get_Crypto_Price import get_crypto_price



def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value))) 

def hide_banner(driver):
    """
    Функция для скрытия баннера на веб-странице.
    """
    try:
        # Поиск элемента баннера по CSS-селектору
        banner = driver.find_element(By.CSS_SELECTOR, '.ant-modal-root .ant-modal-wrap')

        # Нажимаем на кнопку баннера
        banner_button = banner.find_element(By.CSS_SELECTOR, 'div.ant-modal-custom-content button.ant-btn-primary')
        banner_button.click()
        print("Баннер успешно закрыт.")
    except NoSuchElementException:
        print("Баннер не найден или не может быть закрыт.")

def hide_second_banner(driver):
    """
    Функция для скрытия второго баннера на веб-странице.
    """
    try:
        # Находим элемент баннера по CSS-селектору
        banner = driver.find_element(By.CSS_SELECTOR, '#campaign-wrapper')

        # Выполняем скрипт JavaScript для скрытия элемента
        driver.execute_script("arguments[0].style.display = 'none';", banner)
        
        print("Второй баннер успешно скрыт.")
    except NoSuchElementException:
        print("Второй баннер не найден или не может быть скрыт.")




def go_to_next_page(driver):
    try:
        # Находим текущую активную страницу
        current_page = driver.find_element(By.CSS_SELECTOR, 'li.pagination-item-active a').text
        
        # Преобразуем текущую страницу в число
        current_page_number = int(current_page)
        
        # Формируем CSS-селектор для следующей страницы
        next_page_selector = f'li.pagination-item-{current_page_number + 1} a'
        
        # Находим кнопку следующей страницы
        next_page_button = driver.find_element(By.CSS_SELECTOR, next_page_selector)
        
        # Нажимаем на кнопку следующей страницы
        next_page_button.click()
        print(f"Переход на следующую страницу {current_page_number + 1}")
        return True
    except NoSuchElementException:
        print("Следующая страница не найдена.")
        return False

def extract_trade_class(url):
    # Разделение URL по символу ?
    parts = url.split('?')
    if len(parts) < 2:
        return "unknown"  # Возвращаем "unknown", если нет параметров в URL

    params = parts[1].split('&')
    action_type = None
    token = None
    fiat = None

    for param in params:
        key, value = param.split('=')
        if key == 'actionType':
            action_type = value
        elif key == 'token':
            token = value
        elif key == 'fiat':
            fiat = value

    # Преобразование actionType в "buy" или "sell"
    trade_action = "buy" if action_type == "1" else "sell" if action_type == "0" else "unknown"

    # Преобразование токена и фиата в нижний регистр
    token = token.lower() if token else "unknown"
    fiat = fiat.lower() if fiat else "unknown"

    # Сборка строки и возврат результата
    return f"{trade_action}-{token}-{fiat}"

def save_sellers_info(sellers_info, save_path):
    # Проверяем, существует ли файл JSON, и загружаем данные из него, если он уже существует
    existing_data = []
    if os.path.exists(save_path):
        with open(save_path, "r") as file:
            existing_data = json.load(file)

    # Объединяем существующие данные с новыми данными
    existing_data.extend(sellers_info)

    # Сохраняем обновленные данные в JSON файл
    with open(save_path, "w") as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

def scrape_sellers_info(driver, trade_class, market_rate, date_scraping):
    # Ожидание загрузки страницы
    driver.implicitly_wait(10)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")

    # Получение HTML-кода страницы
    html = driver.page_source

    # Создание объекта BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(html, "html.parser")

    # Инициализация списка для хранения информации о продавцах
    sellers_info = []

    # Поиск всех блоков с информацией о продавцах
    seller_blocks = soup.select("div.trade-list__content > div > div.ant-spin-nested-loading.trade-table__spin.css-7o12g0 > div > table > tbody.trade-table__tbody > tr")

    # # Парсинг информации о каждом продавце
    for seller_block in seller_blocks:
        seller_info = {}

        #Добавление сигнатур
        seller_info["data"] = date_scraping
        seller_info["market_rate"] = market_rate
        
        # Извлечение имени продавца и ссылки
        name_element = seller_block.find("div", class_="advertiser-name")
        if name_element:
            seller_info["name_of_trader"] = name_element.find("span").text.strip()
            seller_info["trader_link"] = "unknow"

            # Извлечение цены
            price_element = seller_block.find("span", class_="price-amount")
            if price_element:
                price_text = price_element.text.strip()

                # Удаляем запятые, которые визуально выделяют тысячи
                price = price_text.replace(',', '')

                # Сохраняем цену
                seller_info["price"] = price




        # Извлечение stock 

        item_elements = seller_block.find_all("div", class_="ant-space-item")

        for item_element in item_elements:
            ql_value_element = item_element.find("div", class_="ql-value")
            
            if ql_value_element:
                text = ql_value_element.text.strip()

                if any(currency in text for currency in ["USDT", "ETH", "BTC"]):
                    value = '{:,.4f}'.format(float(text.split()[0].replace(',', '')))
                    currency = text.split()[1]
                    seller_info["stock"] = f"{value} {currency}"
                    break

        # Извлечение лимита
        volume_elements = seller_block.find_all("div", class_="ant-space css-7o12g0 ant-space-horizontal ant-space-align-center")

        for volume_element in volume_elements:
            item_elements = volume_element.find_all("div", class_="ant-space-item")

            for item_element in item_elements:
                inner_volume_element = item_element.find("div", class_="ant-space css-7o12g0 ant-space-vertical")

                if inner_volume_element:
                    ql_values = inner_volume_element.find_all("div", class_="ql-value")

                    for ql_value in ql_values:
                        text = ql_value.text.strip()
                        match = re.match(r"([\d.,]+)\s*~\s*([\d.,]+)\s*([^~]*)", text)

                        if match:
                            value1, value2, currency = match.groups()

                            # Убираем неразрывные пробелы и лишние символы из значений
                            value1 = value1.replace('\xa0', '').replace(',', '')
                            value2 = value2.replace('\xa0', '').replace(',', '')

                            # Берем последнее значение диапазона
                            limit_value = value2

                            # Убираем запятые для визуального разделения тысяч
                            limit_value_formatted = limit_value.replace(',', '')

                            # Формируем строку лимита
                            limit = f"{limit_value_formatted}"
                            seller_info["limit"] = limit


        
        # Извлечение способа оплаты
        payment_elements = seller_block.find_all("div", class_="ant-space css-7o12g0 ant-space-horizontal ant-space-align-center")

        payment_methods = []

        for payment_element in payment_elements:
            item_elements = payment_element.find_all("div", class_="ant-space-item")
    
            for item_element in item_elements:
                tag_wrapper = item_element.find("div", class_="trade-list-tag-wrapper css-7o12g0 ant-tooltip-custom bds-theme-component-light")
        
                if tag_wrapper:
                    tag_elements = tag_wrapper.find_all("div", class_="trade-list-tag")
            
                    for tag_element in tag_elements:
                        payment_methods.append(tag_element.text.strip())

        seller_info["payment_method"] = payment_methods
        
        #Добавление маркера биржы
        seller_info["market"] = "ByBit"

        # Добавление информации о продавце в список
        seller_info["trade_class"] = trade_class  # Добавление класса торговли
        sellers_info.append(seller_info)

    return sellers_info


def main():
    base_url = "https://www.bybit.com/fiat/trade/otc/?"
    tokens = ["USDT", "BTC", "ETH"]
    actions = ["actionType=1", "actionType=0"]
    fiats = ["USD", "RUB"]
    urls = [f"{base_url}{action}&token={token}&fiat={fiat}" for action in actions for token in tokens for fiat in fiats]

    for url in urls:
        print(f"Поиск информации на странице: {url}")
        driver = webdriver.Chrome()
        driver.maximize_window()  # Максимизируем окно браузера
        driver.get(url)
        time.sleep(1)
        wait_for_element(driver, By.CSS_SELECTOR, 'li.pagination-item')
        wait_for_element(driver, By.CSS_SELECTOR, 'li.pagination-next')
        hide_banner(driver)
        time.sleep(1)

        hide_second_banner(driver)
        trade_class = extract_trade_class(driver.current_url)

        # Получаем текущий курс с CoinGeco.com
        price, pair = get_crypto_price(trade_class)
        market_rate = str(price)
        # Получаем текущую дату
        now = datetime.datetime.now()
        date_scraping = now.strftime("%d/%m/%Y")



        # Прокрутка страницы до нужного места
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
        time.sleep(0.5)
        
        page_counter = 1

        while True:
            sellers_info = scrape_sellers_info(driver, trade_class, market_rate, date_scraping)

            # Текущая директория
            save_directory = os.getcwd() 
            # Путь для сохранения файла JSON
            save_path = os.path.join(save_directory, "sellers_info_bybit.json")


            save_sellers_info(sellers_info, save_path)


            time.sleep(0.5)
            if not go_to_next_page(driver):
                break
            page_counter += 1
        print(f"Раздел: {trade_class}. Обработано {page_counter} страниц")
        driver.quit()

if __name__ == "__main__":
    main()
