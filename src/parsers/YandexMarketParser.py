import json
import os
import sys
from tqdm import tqdm
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .AbtractParser import AbstractParser
from .AbtractParser import Loading_Source_Data



class YandexMarketParser(AbstractParser):

    def _run_once(self):
        # Проверяем, был ли метод вызван ранее
        if self._is_first_instance():

            # Получение текущей даты и времени
            current_time = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")

            # Формирование пути для файла
            directory = "./data/JSON/YandexMarketData"
            filename = f"YandexMarketData_{current_time}.json"
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

    def _entering_reques(self):
        # sleep(3)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class="ds-button ds-button_variant_text ds-button_type_primary ds-button_size_m ds-button_brand_market"]'))
            )
            self.driver.find_element(By.CSS_SELECTOR,
                                     '[class="ds-button ds-button_variant_text ds-button_type_primary ds-button_size_m ds-button_brand_market"]').click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class="PreviousStepButton PreviousStepButton_alignVertical"]'))
            )
            self.driver.find_element(By.CSS_SELECTOR,
                                     '[class="PreviousStepButton PreviousStepButton_alignVertical"]').click()
            # self._wait_for_debug()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class="_3TbaT mini-suggest__input"]'))
            )
            self.driver.find_element(By.CSS_SELECTOR, '[class="_3TbaT mini-suggest__input"]').send_keys(self.request)
            self.driver.find_element(By.CSS_SELECTOR, '[class="_30-fz button-focus-ring MySdj _1VU42 _2rdh3 mini-suggest__button"]').click()
        except Exception as e:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[class="_3TbaT mini-suggest__input"]'))
                )
                self.driver.find_element(By.CSS_SELECTOR, '[class="_3TbaT mini-suggest__input"]').send_keys(self.request)
                self.driver.find_element(By.CSS_SELECTOR, '[class="_30-fz button-focus-ring MySdj _1VU42 _2rdh3 mini-suggest__button"]').click()
            except Exception as e:
                print('Ошибка на этапе входа на сайт')

    def _pars_page(self):
        self.new_data = []

        # Ожидание загрузки списка товаров
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-apiary-widget-name="@marketfront/SerpEntity"]'))
            )
        except Exception as e:
            print(f"Ошибка ожидания списка товаров")
            return

        titles = self.driver.find_elements(By.CSS_SELECTOR, '[data-apiary-widget-name="@marketfront/SerpEntity"]')

        for title in titles:
            try:
                # Ожидание заголовка внутри текущего блока
                description_element = WebDriverWait(title, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[itemprop="name"]'))
                )
                description = description_element.text.strip()

                # Получение URL товара
                try:
                    url_element = title.find_element(By.CSS_SELECTOR, 'a.EQlfk.Gqfzd')
                    url = url_element.get_attribute('href')
                except Exception:
                    url = "Ссылка не найдена"

                # Ожидание и получение цены
                try:
                    price_element = WebDriverWait(title, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'span.ds-text.ds-text_weight_bold'))
                    )
                    price = price_element.text.strip().replace("\u202f", "")  # Убираем неразрывные пробелы
                except Exception:
                    price = "Цена не найдена"

                # Получение ID карточки (из <article>)
                try:
                    card_id = title.find_element(By.TAG_NAME, "article").get_attribute("id")
                except Exception:
                    card_id = "ID не найден"

                # Формирование данных
                data = {
                    'description': description,
                    'url': url,
                    'price': price,
                    'card_id': card_id
                }
                print('Карточка товара обработана')
                # Фильтрация по ключевым словам
                if any(item.lower() in description.lower() for item in self.items):
                    self.new_data.append(data)
                    print('Карточка товара добавлена в JSON')
                    # print(data, "\n")

            except Exception as e:
                print(f"Ошибка обработки карточки товара")
                continue

    def parse(self):
        self._setup()
        self._get_url()
        self._entering_reques()
        self._load_data()
        self._pars_page()
        self._add_request()
        self._save_data()


# if __name__ == '__main__':
#     try:
#         articles = list(Loading_Source_Data('../../Рабочий.xlsx').loading_articles())
#         AbstractParser.clear_terminal()
#         progress_bar = tqdm(articles, desc="Обработка артикулов", unit="шт", ncols=80, ascii=True)
#
#         for article in progress_bar:
#             sys.stdout.flush()  # Принудительное обновление потока (важно для PyCharm!)
#             print(f"\n\033[1;32;4mПарсится сайт Yandex Market\033[0m\n")
#             print(f"\n\033[1;32;4mПоиск артикула: {article}\033[0m\n")
#
#             parser = YandexMarketParser(url='https://market.yandex.ru/',
#                                         request=article,
#                                         items=[article, 'Можно добавить что угодно'])
#             parser.parse()
#             parser.clear_terminal()
#     except Exception as e:
#         print('Ошибка при создании объекта парсинга')



