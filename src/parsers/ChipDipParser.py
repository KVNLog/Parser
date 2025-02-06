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
        """Создаёт JSON-файл с данными, если метод вызывается впервые."""
        from src.logger import parser_logger
        try:
            if self._is_first_instance():
                parser_logger.info(f"{self.__class__.__name__}: Первый вызов _run_once(), создаём JSON-файл")

                # Получение текущей даты и времени
                current_time = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")

                # Формирование пути для файла
                directory = "./data/JSON/ChipDipData"
                filename = f"ChipDipData_{current_time}.json"
                AbstractParser._filepath = os.path.join(directory, filename)
                parser_logger.debug(
                    f"{self.__class__.__name__}: JSON-файл будет сохранён по пути: {AbstractParser._filepath}")

                # Создание директории, если её нет
                os.makedirs(directory, exist_ok=True)
                parser_logger.info(f"{self.__class__.__name__}: Директория проверена/создана: {directory}")

                # Формирование данных для записи в JSON
                metadata = {
                    "Дата и время создания файла": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "Данные": self.data  # Если `self.data` пустой, сохраняется пустой объект
                }

                # Запись данных в файл
                with open(AbstractParser._filepath, 'w', encoding='utf-8') as file:
                    json.dump(metadata, file, ensure_ascii=False, indent=4)

                parser_logger.info(
                    f"{self.__class__.__name__}: Файл {filename} успешно создан, записано {len(self.data)} записей")

            else:
                parser_logger.warning(
                    f"{self.__class__.__name__}: Метод _run_once() уже был вызван ранее, повторный запуск игнорируется")

            print(self._is_first_instance())

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при выполнении _run_once(): {e}")

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    def _entering_request(self):
        """Вводит запрос в строку поиска и нажимает кнопку поиска."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Начало ввода запроса '{self.request}'")

            # Ожидание появления поля ввода
            search_input_locator = (By.CSS_SELECTOR, '[class="header__input header__search-input auc__input"]')
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(search_input_locator))
            parser_logger.debug(f"{self.__class__.__name__}: Поле ввода поиска найдено")

            # Ввод запроса
            self.driver.find_element(*search_input_locator).send_keys(self.request)
            parser_logger.info(f"{self.__class__.__name__}: Запрос '{self.request}' введён в строку поиска")

            # Ожидание появления кнопки поиска
            search_button_locator = (By.CSS_SELECTOR, '[class="btn-reset header__button header__search-button"]')
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(search_button_locator))
            parser_logger.debug(f"{self.__class__.__name__}: Кнопка поиска найдена")

            # Клик по кнопке поиска
            self.driver.find_element(*search_button_locator).click()
            parser_logger.info(f"{self.__class__.__name__}: Поиск по запросу '{self.request}' успешно выполнен")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка на этапе ввода запроса '{self.request}': {e}")

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    def _pars_page(self):
        """Парсит товары на странице и сохраняет данные."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Начало парсинга страницы")

            self.new_data = []
            self.url_list = []

            # Ожидание загрузки списка товаров
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[class="with-hover"]'))
                )
                titles = self.driver.find_elements(By.CSS_SELECTOR, '[class="with-hover"]')
                parser_logger.info(f"{self.__class__.__name__}: Найдено {len(titles)} карточек товаров")
            except Exception as e:
                parser_logger.exception(f"{self.__class__.__name__}: Ошибка ожидания списка товаров: {e}")
                return

            for title in titles:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'b'))
                    )
                    name = title.find_element(By.CSS_SELECTOR, 'b').text
                except Exception:
                    name = 'Имя не найдено'
                    parser_logger.warning(f"{self.__class__.__name__}: Имя товара не найдено")

                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'a'))
                    )
                    description = title.find_element(By.CSS_SELECTOR, 'a').get_attribute('innerText')
                except Exception:
                    description = 'Описание не загружено'
                    parser_logger.warning(f"{self.__class__.__name__}: Описание товара не загружено")

                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[class="link"]'))
                    )
                    url = title.find_element(By.CSS_SELECTOR, '[class="link"]').get_attribute('href')
                except Exception:
                    url = "Ссылка не найдена"
                    parser_logger.warning(f"{self.__class__.__name__}: Ссылка на товар не найдена")

                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'span.price-main > span'))
                    )
                    price = title.find_element(By.CSS_SELECTOR, 'span.price-main > span').text
                except Exception:
                    price = "Цена не найдена"
                    parser_logger.warning(f"{self.__class__.__name__}: Цена товара не найдена")

                cards_ID = title.get_attribute('id') if title.get_attribute('id') else "ID не найден"

                data = {
                    'name': name,
                    'description': description,
                    'url': url,
                    'price': price,
                    'cards_ID': cards_ID
                }

                self.new_data.append(data)
                self.url_list.append(data['url'])
                parser_logger.debug(f"{self.__class__.__name__}: Добавлена карточка товара: {data}")

            parser_logger.info(
                f"{self.__class__.__name__}: Парсинг завершён, всего обработано {len(self.new_data)} карточек")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при парсинге страницы: {e}")

    def _get_datasheet(self):
        """Извлекает ссылки на даташиты (PDF) с каждой страницы товаров."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Начало сбора даташитов для {len(self.url_list)} товаров")

            self.datasheet_list = []

            for url in self.url_list:
                try:
                    parser_logger.info(f"{self.__class__.__name__}: Загрузка страницы: {url}")
                    self.driver.get(url)

                    # Пытаемся найти ссылку на даташит
                    datasheet_url = self.driver.find_element(
                        By.CSS_SELECTOR, '[class="link download__link with-pdfpreview"]'
                    ).get_attribute('href')

                    self.datasheet_list.append(datasheet_url)
                    parser_logger.debug(f"{self.__class__.__name__}: Даташит найден: {datasheet_url}")

                except Exception as e:
                    parser_logger.warning(f"{self.__class__.__name__}: Даташит не найден на странице: {url}")
                    self.datasheet_list.append(None)  # Добавляем None, если нет даташита

                sleep(1)  # Задержка для предотвращения бана

            parser_logger.info(
                f"{self.__class__.__name__}: Сбор даташитов завершён, найдено {len([d for d in self.datasheet_list if d])} PDF")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при сборе даташитов: {e}")

    def _add_datasheet(self):
        """Добавляет ссылки на даташиты к данным о товарах."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Начало добавления даташитов к товарам")

            if len(self.new_data) != len(self.datasheet_list):
                parser_logger.warning(
                    f"{self.__class__.__name__}: Количество товаров ({len(self.new_data)}) не совпадает с количеством даташитов ({len(self.datasheet_list)})")

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

                if self.datasheet_list[ind]:
                    parser_logger.debug(
                        f"{self.__class__.__name__}: Даташит добавлен: {self.datasheet_list[ind]} → {data['name']}")
                else:
                    parser_logger.warning(f"{self.__class__.__name__}: У товара '{data['name']}' отсутствует даташит")

            parser_logger.info(f"{self.__class__.__name__}: Даташиты успешно добавлены к {len(self.data)} товарам")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при добавлении даташитов: {e}")

    def parse(self):
        """Запускает полный цикл парсинга данных."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Начало парсинга")

            self._setup()
            parser_logger.info(f"{self.__class__.__name__}: WebDriver успешно настроен")

            self._get_url()
            parser_logger.info(f"{self.__class__.__name__}: Загружен сайт {self.url}")

            self._entering_request()
            parser_logger.info(f"{self.__class__.__name__}: Поисковый запрос '{self.request}' отправлен")

            self._load_data()
            parser_logger.info(f"{self.__class__.__name__}: Загружены предыдущие данные (если есть)")

            self._pars_page()
            parser_logger.info(
                f"{self.__class__.__name__}: Парсинг страницы завершён, найдено {len(self.new_data)} товаров")

            self._get_datasheet()
            parser_logger.info(f"{self.__class__.__name__}: Даташиты собраны для {len(self.datasheet_list)} товаров")

            self._add_datasheet()
            parser_logger.info(f"{self.__class__.__name__}: Даташиты добавлены к товарам")

            self._add_request()
            parser_logger.info(f"{self.__class__.__name__}: Новые данные добавлены в JSON")

            self._save_data()
            parser_logger.info(f"{self.__class__.__name__}: Данные успешно сохранены")

            parser_logger.info(f"{self.__class__.__name__}: Парсинг завершён, обработано {len(self.data)} товаров")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка во время парсинга: {e}")

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