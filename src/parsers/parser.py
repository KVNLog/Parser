import json
from time import sleep

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramRetryAfter
import asyncio




class Parser:
    def __init__(self, url, request, items=[], number_pages=100, version_chrome=None, telegram_sender=None):
        self.url = url
        self.request = request
        self.items = items
        self.number_pages = number_pages
        self.version_chrome = version_chrome
        self.data = []
        self.telegram_sender = telegram_sender

    def _setup(self):
        chrome_options = Options()
        chrome_options.page_load_strategy = 'eager'
        self.driver = uc.Chrome(options=chrome_options, headless=False, use_subprocess=False, version_main=self.version_chrome) # headless=True - тихий режим, браузер не запускается

    def _get_url(self):
        self.driver.get(self.url)

    def _entering_reques(self):
        self.driver.find_element(By.CLASS_NAME,'styles-module-input-rA1dB').send_keys(self.request)
        self.driver.find_element(By.CSS_SELECTOR, '[data-marker = "search-form/submit-button"]').click()

    def _load_data(self):
        with open('data.json', 'r', encoding='utf-8') as file:
            # Проверка на пустой файл перед загрузкой данных
            file_data = file.read()
            if file_data:
                self.data = json.loads(file_data)
            else:
                self.data = []

    def _paginator(self):
        while self.driver.find_elements(By.CSS_SELECTOR, '[data-marker="pagination-button/nextPage"]') and self.number_pages >= 0:
            self._pars_page()
            self.driver.find_element(By.CSS_SELECTOR, '[data-marker="pagination-button/nextPage"]').click()
            self.number_pages -= 1

    def _pars_page(self):
        titles = self.driver.find_elements(By.CSS_SELECTOR, '[data-marker="item"]')
        for title in titles:
            name = title.find_element(By.CSS_SELECTOR, '[itemprop="name"]').text
            # description = title.find_element(By.CSS_SELECTOR, '[class*=styles-module-root]').text
            description = title.find_element(By.CSS_SELECTOR, '[itemprop="description"]').get_attribute('content')
            url = title.find_element(By.CSS_SELECTOR, '[data-marker="item-title"]').get_attribute('href')
            price = title.find_element(By.CSS_SELECTOR, '[itemprop="price"]').get_attribute('content')
            # cards_ID = title.find_element(By.CSS_SELECTOR, '[data-marker="item"]').get_attribute('id')
            cards_ID = title.get_attribute('data-item-id')
            data = {
                'name': name,
                'description': description,
                'url': url,
                'price': price,
                'cards_ID': cards_ID
            }
            existing_ids = [card['cards_ID'] for card in self.data]
            if not data['cards_ID'] in existing_ids:
                if any(item.lower() in description.lower() or item.lower() in name.lower() for item in self.items):
                    self.data.append(data)
                    self.new_data.append(data)
                    print(data)
                    print('\n')


    def _save_data(self):
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def parse(self):
        self._setup()
        self._get_url()
        self._entering_reques()
        self._load_data()
        # self._paginator()
        self._pars_page()
        self._save_data()
        # asyncio.run(self.telegram_sender.send_data(self.new_data))
        self.driver.quit()

class TelegramSender:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id

    async def send_data(self, data):
        for item in data:
            message = (
                f"Название: {item['name']}\n"
                f"Описание: {item['description']}\n"
                f"Ссылка: {item['url']}\n"
                f"Цена: {item['price']}\n"
            )
            try:
                await self.bot.send_message(chat_id=self.chat_id, text=message)
                await asyncio.sleep(1)
            except TelegramRetryAfter as e:
                print(f"Hit rate limit, retrying in {e.timeout} seconds")
                await asyncio.sleep(e.timeout)
                await self.bot.send_message(chat_id=self.chat_id, text=message)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # # Инициализация бота
    # API_TOKEN = ''  # @kvn_avoto_bot
    # CHAT_ID = ''
    # session = AiohttpSession()
    # bot = Bot(token=API_TOKEN, session=session)
    #
    # # Создание отправителя
    # telegram_sender = TelegramSender(bot, CHAT_ID)

    parser = Parser(url='https://www.avito.ru/',
                         request='6ES7500-0HP00-0AB0',
                         items = ['6ES7500-0HP00-0AB0'],
                         number_pages = 2,
                         version_chrome = 131
                         # telegram_sender=telegram_sender
                         )

    parser.parse()