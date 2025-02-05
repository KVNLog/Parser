import json
import os
import sys
from tqdm import tqdm
from datetime import datetime
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .AbtractParser import AbstractParser
from .AbtractParser import Loading_Source_Data


class CipDipParser(AbstractParser):

    def _run_once(self):
        # Проверяем, был ли метод вызван ранее
        if self._is_first_instance():

            # Получение текущей даты и времени
            current_time = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")

            # Формирование пути для файла
            directory = "./data/JSON/ChipDipData"
            filename = f"ChipDipData_{current_time}.json"
            AbstractParser._filepath = os.path.join(directory, filename)

            # Создание директории, если она не существует
            os.makedirs(directory, exist_ok=True)

            # Формирование данных для записи в JSON
            metadata = {
                "Дата и время создания файла": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "Данные": self.data  # Если `self.data` пустой, сохраняется пустой объект
            }

            # Запись данных в файл в формате JSON
            with open(AbstractParser._filepath, 'w', encoding='utf-8') as file:
                json.dump(metadata, file, ensure_ascii=False, indent=4)
        else:
            pass
        print(self._is_first_instance())

    def _entering_reques(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '[class="header__input header__search-input auc__input"]'))
            )
            self.driver.find_element(By.CSS_SELECTOR, '[class="header__input header__search-input auc__input"]').send_keys(self.request)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '[class="btn-reset header__button header__search-button"]'))
            )
            self.driver.find_element(By.CSS_SELECTOR, '[class="btn-reset header__button header__search-button"]').click()
        except Exception as e:
            print('Ошибка на этапе входа на сайт')

    def _pars_page(self):
        self.new_data = []
        self.url_list = []
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class="with-hover"]'))
            )
            titles = self.driver.find_elements(By.CSS_SELECTOR, '[class="with-hover"]')
        except Exception as e:
            print(f"Ошибка ожидания списка товаров")

        for title in titles:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'b'))
                )
                name = title.find_element(By.CSS_SELECTOR, 'b').text
            except Exception as e:
                name = 'Имя не найдено'

            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a'))
                )
                description = title.find_element(By.CSS_SELECTOR, 'a').get_attribute('innerText')
            except Exception as e:
                description = 'Описание не загружено'

            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[class="link"]'))
                )
                url =  title.find_element(By.CSS_SELECTOR, '[class="link"]').get_attribute('href')
            except Exception as e:
                url = "Ссылка не найдена"

            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'span.price-main > span'))
                )
                price = title.find_element(By.CSS_SELECTOR, 'span.price-main > span').text
            except Exception as e:
                price = "Цена не найдена"

            cards_ID = title.get_attribute('id')
            data = {
                'name': name,
                'description': description,
                'url': url,
                'price': price,
                'cards_ID': cards_ID
            }

            self.new_data.append(data)
            self.url_list.append(data['url'])
            print('Карточка товара добавлена в JSON')
            print('\n')

    def _get_datasheet(self):
        self.datasheet_list = []

        for url in self.url_list:
            try:
                self.driver.get(url)
                # Пытаемся найти элемент и получить его атрибут
                datasheet_url = self.driver.find_element(By.CSS_SELECTOR,
                                                         '[class="link download__link with-pdfpreview"]').get_attribute(
                                                                                                                 'href')
                self.datasheet_list.append(datasheet_url)
            except Exception as e:
                # Если элемент не найден, добавляем None или пропускаем
                print(f"Element not found on page: {url}")
                self.datasheet_list.append(None)  # Или просто пропускайте append
            sleep(1)
        print(self.datasheet_list)

    def _add_datasheet(self):
        self.data = []
        for ind, data in enumerate(self.new_data):
            new_data = {
                'name': data['name'],
                'description': data['description'],
                'url': data['url'],
                'price': data['price'],
                'cards_ID': data['cards_ID'],
                'datasheet': self.datasheet_list[ind]
            }
            self.data.append(new_data)

    def parse(self):
        self._setup()
        self._get_url()
        self._entering_reques()
        self._load_data()
        self._pars_page()
        self._get_datasheet()
        self._add_datasheet()
        self._add_request()
        self._save_data()


# if __name__ == '__main__':
#     articles = list(Loading_Source_Data('../../Рабочий.xlsx').loading_articles())
#     AbstractParser.clear_terminal()
#     progress_bar = tqdm(articles, desc="Обработка артикулов", unit="шт", ncols=80, ascii=True)
#
#     for article in progress_bar:
#         try:
#             sys.stdout.flush()  # Принудительное обновление потока (важно для PyCharm!)
#             print(f"\n\033[1;32;4mПарсится сайт ChipDip\033[0m\n")
#             print(f"\n\033[1;32;4mПоиск артикула: {article}\033[0m\n")
#
#             parser = CipDipParser(url='https://www.chipdip.ru/',
#                                request=article,
#                                items=[article, 'Можно добавить что угодно'])
#             parser.parse()
#             parser.clear_terminal()
#         except Exception as e:
#             print('Ошибка при создании объекта парсинга')