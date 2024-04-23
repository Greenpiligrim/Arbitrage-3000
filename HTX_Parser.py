#__________не______трогать__________работает!!!______
#этот скрипт проходит повсем страницам сайта биржи https://www.htx.com собирает информацию и в конце сохраняет все в джейсон,
#затем программа переходит по следующейссылке и парсит следующую страницу пока не пройдет по всем

import datetime
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Get_Crypto_Price import get_crypto_price


# Определение явных ожиданий для загрузки элемента
def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

# Определение явных ожиданий для скрытия модального окна
def wait_for_modal_to_hide(driver, timeout=10):
    return WebDriverWait(driver, timeout).until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, '.hb-modal.en')))

# Определение явных ожиданий для перехода на следующую страницу
def wait_for_next_page(driver, current_url, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.url_changes(current_url))

def hide_modal(driver):
    modal = driver.find_elements(By.CSS_SELECTOR, '.hb-modal.en')
    if modal:
        driver.execute_script("arguments[0].style.display = 'none';", modal[0])
        print("Блок успешно скрыт.")
    else:
        print("Элемент с классом 'hb-modal en' не найден.")

def scrape_sellers_info(driver, trade_class, date_scraping, market_rate):
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
    seller_blocks = soup.find_all("div", class_="info-wrapper")

    # Парсинг информации о каждом продавце
    for seller_block in seller_blocks:
        seller_info = {}

        #Добавление сигнатур
        seller_info["data"] = date_scraping
        seller_info["market_rate"] = market_rate
        
        # Извлечение имени продавца и ссылки
        name_element = seller_block.find("h3", class_="font14")
        if name_element:
            seller_info["name_of_trader"] = name_element.text.strip()
            trader_link = name_element.find_parent("a")["href"].split('/')[-1]
            seller_info["trader_link"] = trader_link
        
        # Извлечение цены
        # price_element = seller_block.find("div", class_="width210 price average mr-24")
        # if price_element:
        #     seller_info["price"] = price_element.text.strip()
        # Извлечение цены
        price_element = seller_block.find("div", class_="width210 price average mr-24")
        if price_element:
            price_text = price_element.text.strip()
            # Преобразование цены в число и форматирование
            try:
                price = float(price_text.split()[0].replace(',', ''))  # Удаляем запятые и конвертируем в float
                seller_info["price"] = '{:.2f}'.format(price)  # Форматируем цену с двумя знаками после запятой
            except ValueError:
                print("Ошибка: Невозможно преобразовать цену в число.")

        # Извлечение объема и лимита
            volume_element = seller_block.find("div", class_="limit-box")
            if volume_element:
                stock_element = volume_element.find("div", class_="stock")
                limit_element = volume_element.find("div", class_="limit")

                if stock_element:
                    stock_text = stock_element.text.strip()
                    stock_value, stock_currency = stock_text.split()
                    # Добавляем запятые для визуального разделения тысяч
                    stock_formatted = '{:,.6f}'.format(float(stock_value))
                    stock = f"{stock_formatted} {stock_currency}"
                    seller_info["stock"] = stock

                if limit_element:
                    limit_text = limit_element.text.strip()
                    # Разделяем лимит на две части: значение и валюту
                    limit_value_span, limit_currency_span = limit_element.find_all("span")
                    # Извлекаем значения
                    first_limit_value = limit_value_span.text.strip().replace(',', '')  # Убираем запятые
                    second_limit_value = limit_currency_span.text.strip().split()[0]  # Берем первое число после минуса
                    # Форматируем значения
                    limit_value = second_limit_value.replace(',', '')  # Убираем запятые
                    # Проверяем наличие минуса и заменяем его на тире
                    if '-' in limit_text:
                        limit_value = limit_value[1:]  # Убираем тире перед числом
                    # Формируем строку лимита
                    limit = f"{limit_value}"
                    seller_info["limit"] = limit





        
        # Извлечение способа оплаты
        payment_element = seller_block.find("div", class_="way width256")
        if payment_element:
            payment_methods = [method.strip() for method in payment_element.text.split('\n') if method.strip()]
            seller_info["payment_method"] = payment_methods

        #Добавление маркера биржы
        seller_info["market"] = "HTX"
        
        # Добавление информации о продавце в список
        seller_info["trade_class"] = trade_class  # Добавление класса торговли
        sellers_info.append(seller_info)

    return sellers_info

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

def go_to_next_page(driver):
    try:
        # Находим элемент кнопки "Next Page"
        next_page_button = driver.find_element(By.CSS_SELECTOR, 'li.ivu-page-next')
        
        # Проверяем, если класс кнопки содержит "ivu-page-disabled", то кнопка отключена
        if 'ivu-page-disabled' in next_page_button.get_attribute('class'):
            print("Кнопка 'Next Page' отключена.")
            return False
        
        # Нажимаем на кнопку "Next Page"
        next_page_button.click()
        print("Кнопка 'Next Page' успешно нажата.")
        return True
    except:
        print("Кнопка 'Next Page' не найдена или не может быть нажата.")
        return False

def extract_trade_class(url):
    # Разделение URL по символу /
    parts = url.rstrip('/').split('/')
    # Возвращение последней части URL
    return parts[-2] if parts[-1] == '' else parts[-1]

def main():
    # Массив ссылок для прохода
    base_url = "https://www.htx.com/en-us/fiat-crypto/trade/"
    currencies = ["usdt", "btc", "eth"]
    actions = ["buy", "sell"]
    urls = [f"{base_url}{action}-{currency}-{fiat}/" for action in actions for currency in currencies for fiat in ["usd", "rub"]]

    for url in urls:
        print(f"Поиск информации на странице: {url}")

        driver = webdriver.Chrome()
        driver.maximize_window()  # Максимизируем окно браузера
        driver.get(url)
        time.sleep(1)
        hide_modal(driver)
        trade_class = extract_trade_class(driver.current_url)

        # Получаем текущий курс с CoinGeco.com
        price, pair = get_crypto_price(trade_class)
        market_rate = str(price)
        # Получаем текущую дату
        now = datetime.datetime.now()
        date_scraping = now.strftime("%d/%m/%Y")

        while True:
            # Ожидание загрузки страницы и скрытия модального окна
            wait_for_element(driver, By.CSS_SELECTOR, 'div.info-wrapper')
            wait_for_modal_to_hide(driver)

            # Прокрутка страницы до нужного места
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
            time.sleep(1)

            sellers_info = scrape_sellers_info(driver, trade_class, date_scraping, market_rate)

            # Путь для сохранения файла JSON
            save_directory = os.getcwd()  # Текущая директория

            # Путь для сохранения файла JSON
            save_path = os.path.join(save_directory, "sellers_info_htx.json")
            save_sellers_info(sellers_info, save_path)
            current_url = driver.current_url

            # Переход на следующую страницу
            if not go_to_next_page(driver):
                break

            # Ожидание загрузки следующей страницы
            # wait_for_next_page(driver, current_url)

        # Закрытие браузера после обработки всех страниц для текущей ссылки
        driver.quit()

if __name__ == "__main__":
    main()
