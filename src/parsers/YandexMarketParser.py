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
        """Создаёт JSON-файл с данными, если метод вызывается впервые."""
        from src.logger import parser_logger
        try:
            if self._is_first_instance():
                parser_logger.info(f"{self.__class__.__name__}: Первый вызов _run_once(), создаём JSON-файл")

                # Получение текущей даты и времени
                current_time = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")

                # Формирование пути для файла
                directory = "./data/JSON/YandexMarketData"
                filename = f"YandexMarketData_{current_time}.json"
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

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при выполнении _run_once(): {e}")

    def _entering_request(self):
        """Вводит запрос в строку поиска и нажимает необходимые кнопки на сайте."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Начало ввода запроса '{self.request}'")

            # Попытка нажать кнопку "Пропустить" (если есть)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '[class="ds-button ds-button_variant_text ds-button_type_primary ds-button_size_m ds-button_brand_market"]'))
                )
                self.driver.find_element(By.CSS_SELECTOR,
                                         '[class="ds-button ds-button_variant_text ds-button_type_primary ds-button_size_m ds-button_brand_market"]').click()
                parser_logger.info(f"{self.__class__.__name__}: Кнопка 'Пропустить' нажата")
            except Exception:
                parser_logger.warning(f"{self.__class__.__name__}: Кнопка 'Пропустить' не найдена")

            # Попытка нажать кнопку "Назад" (если есть)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '[class="PreviousStepButton PreviousStepButton_alignVertical"]'))
                )
                self.driver.find_element(By.CSS_SELECTOR,
                                         '[class="PreviousStepButton PreviousStepButton_alignVertical"]').click()
                parser_logger.info(f"{self.__class__.__name__}: Кнопка 'Назад' нажата")
            except Exception:
                parser_logger.warning(f"{self.__class__.__name__}: Кнопка 'Назад' не найдена")

            # Ввод поискового запроса
            try:
                search_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[class="_3TbaT mini-suggest__input"]'))
                )
                search_input.send_keys(self.request)
                parser_logger.info(f"{self.__class__.__name__}: Запрос '{self.request}' введён")
            except Exception:
                parser_logger.warning(f"{self.__class__.__name__}: Поле ввода запроса не найдено")

            # Нажатие кнопки "Найти"
            try:
                search_button = self.driver.find_element(By.CSS_SELECTOR,
                                                         '[class="_30-fz button-focus-ring MySdj _1VU42 _2rdh3 mini-suggest__button"]')
                search_button.click()
                parser_logger.info(f"{self.__class__.__name__}: Кнопка 'Найти' нажата")
            except Exception:
                parser_logger.warning(f"{self.__class__.__name__}: Кнопка 'Найти' не найдена")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка на этапе ввода запроса '{self.request}': {e}")

    def _pars_page(self):
        """Парсит товары на странице и сохраняет данные."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Начало парсинга страницы")

            self.new_data = []

            # Ожидание загрузки списка товаров
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '[data-apiary-widget-name="@marketfront/SerpEntity"]'))
                )
                parser_logger.info(f"{self.__class__.__name__}: Найден список товаров")
            except Exception as e:
                parser_logger.exception(f"{self.__class__.__name__}: Ошибка ожидания списка товаров: {e}")
                return

            titles = self.driver.find_elements(By.CSS_SELECTOR, '[data-apiary-widget-name="@marketfront/SerpEntity"]')
            parser_logger.info(f"{self.__class__.__name__}: Найдено {len(titles)} карточек товаров")

            for title in titles:
                try:
                    # Ожидание заголовка внутри текущего блока
                    try:
                        description_element = WebDriverWait(title, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[itemprop="name"]'))
                        )
                        description = description_element.text.strip()
                    except Exception:
                        description = "Описание не найдено"
                        parser_logger.warning(f"{self.__class__.__name__}: Описание товара не найдено")

                    # Получение URL товара
                    try:
                        url_element = title.find_element(By.CSS_SELECTOR, 'a.EQlfk.Gqfzd')
                        url = url_element.get_attribute('href')
                    except Exception:
                        url = "Ссылка не найдена"
                        parser_logger.warning(f"{self.__class__.__name__}: Ссылка на товар не найдена")

                    # Ожидание и получение цены
                    try:
                        price_element = WebDriverWait(title, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.ds-text.ds-text_weight_bold'))
                        )
                        price = price_element.text.strip().replace("\u202f", "")  # Убираем неразрывные пробелы
                    except Exception:
                        price = "Цена не найдена"
                        parser_logger.warning(f"{self.__class__.__name__}: Цена товара не найдена")

                    # Получение ID карточки (из <article>)
                    try:
                        card_id = title.find_element(By.TAG_NAME, "article").get_attribute("id")
                    except Exception:
                        card_id = "ID не найден"
                        parser_logger.warning(f"{self.__class__.__name__}: ID товара не найден")

                    # Формирование данных
                    data = {
                        'description': description,
                        'url': url,
                        'price': price,
                        'card_id': card_id
                    }

                    parser_logger.debug(f"{self.__class__.__name__}: Карточка обработана: {data}")

                    # Фильтрация по ключевым словам
                    if any(item.lower() in description.lower() for item in self.items):
                        self.new_data.append(data)
                        parser_logger.info(f"{self.__class__.__name__}: Карточка товара добавлена в JSON")

                except Exception as e:
                    parser_logger.exception(f"{self.__class__.__name__}: Ошибка обработки карточки товара: {e}")
                    continue

            parser_logger.info(f"{self.__class__.__name__}: Парсинг завершён, обработано {len(self.new_data)} карточек")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при парсинге страницы: {e}")

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

            self._add_request()
            parser_logger.info(f"{self.__class__.__name__}: Новые данные добавлены в JSON")

            self._save_data()
            parser_logger.info(f"{self.__class__.__name__}: Данные успешно сохранены")

            parser_logger.info(f"{self.__class__.__name__}: Парсинг завершён, обработано {len(self.data)} товаров")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка во время парсинга: {e}")

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



