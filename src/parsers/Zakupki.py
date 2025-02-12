import json
import os
import sys
from time import sleep

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from .AbtractParser import AbstractParser
from .AbtractParser import Loading_Source_Data


class Zakupki(AbstractParser):

    def _run_once(self):
        """Создаёт JSON-файл с данными, если метод вызывается впервые."""
        from src.logger import parser_logger
        try:
            if self._is_first_instance():
                parser_logger.info(f"{self.__class__.__name__}: Первый вызов _run_once(), создаём файл JSON")

                # Получение текущей даты и времени
                current_time = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")

                # Формирование пути для файла
                directory = "./data/JSON/Zakupki"
                filename = f"Zakupki_{current_time}.json"
                AbstractParser._filepath = os.path.join(directory, filename)

                parser_logger.debug(
                    f"{self.__class__.__name__}: JSON-файл будет сохранён по пути: {AbstractParser._filepath}")

                # Создание директории, если она не существует
                os.makedirs(directory, exist_ok=True)
                parser_logger.info(f"{self.__class__.__name__}: Директория проверена/создана: {directory}")

                # Формирование данных для записи в JSON
                metadata = {
                    "Дата и время создания файла": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "Данные": self.data  # Если `self.data` пустой, сохраняется пустой объект
                }

                # Запись данных в файл в формате JSON
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
        """
        Вводит запрос в строку поиска и нажимает кнопку поиска Zakupki.
        Проверяет состояние галочек фильрования
        """
        from src.logger import parser_logger

        try:
            # Создание объекта ActionChains
            actions = ActionChains(self.driver)
            sleep(3)
            # Выполнение щелчка мыши в произвольной точке (например, координаты x=10, y=10)
            actions.move_by_offset(10, 10).click().perform()
            parser_logger.info(f"{self.__class__.__name__}: Выполнен щелчок мыши для скрытия информационного окна")
        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при попытке скрыть информационное окно: {e}")

        try:
            parser_logger.info(f"{self.__class__.__name__}: Переход в меню закупки")

            # Находим кнопку закупки
            zakupki_button = self.driver.find_element(By.CSS_SELECTOR,
                                                    '[class="main-link  _order "]')
            zakupki_button.click()

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка на этапе перехода в меню закупки: {e}")

        try:
            parser_logger.info(f"{self.__class__.__name__}: Проверка фильтрования поискового запроса")

            # Функция для клика по чекбоксу с использованием JavaScript
            def click_checkbox(checkbox_element, action_description):
                if checkbox_element.is_selected():
                    self.driver.execute_script("arguments[0].click();", checkbox_element)
                    parser_logger.info(f"{self.__class__.__name__}: {action_description}")
                else:
                    parser_logger.info(f"{self.__class__.__name__}: {action_description} уже деактивирован")

            # Находим и обрабатываем чекбокс "Подача заявок"
            checkbox_podacha_zayavok = self.driver.find_element(By.CSS_SELECTOR, '[id="af"]')
            if not checkbox_podacha_zayavok.is_selected():
                self.driver.execute_script("arguments[0].click();", checkbox_podacha_zayavok)
                parser_logger.info(f"{self.__class__.__name__}: Чекбокс 'Подача заявок' активирован")
            else:
                parser_logger.info(f"{self.__class__.__name__}: Чекбокс 'Подача заявок' уже активен")

            # Находим и обрабатываем чекбокс "Работа комиссии"
            checkbox_rabota_komissii = self.driver.find_element(By.CSS_SELECTOR, '[id="ca"]')
            if not checkbox_rabota_komissii.is_selected():
                self.driver.execute_script("arguments[0].click();", checkbox_rabota_komissii)
                parser_logger.info(f"{self.__class__.__name__}: Чекбокс 'Работа комиссии' активирован")
            else:
                parser_logger.info(f"{self.__class__.__name__}: Чекбокс 'Работа комиссии' уже активен")

            # Находим и обрабатываем чекбокс "Закупка завершена"
            checkbox_zakupka_zavershena = self.driver.find_element(By.CSS_SELECTOR, '[id="pc"]')
            if checkbox_zakupka_zavershena.is_selected():
                self.driver.execute_script("arguments[0].click();", checkbox_zakupka_zavershena)
                parser_logger.info(f"{self.__class__.__name__}: Чекбокс 'Закупка завершена' деактивирован")
            else:
                parser_logger.info(f"{self.__class__.__name__}: Чекбокс 'Закупка завершена' уже деактивирован")

            # Находим и обрабатываем чекбокс "Закупка отменена"
            checkbox_zakupka_otmenena = self.driver.find_element(By.CSS_SELECTOR, '[id="pa"]')
            if checkbox_zakupka_otmenena.is_selected():
                self.driver.execute_script("arguments[0].click();", checkbox_zakupka_otmenena)
                parser_logger.info(f"{self.__class__.__name__}: Чекбокс 'Закупка отменена' деактивирован")
            else:
                parser_logger.info(f"{self.__class__.__name__}: Чекбокс 'Закупка отменена' уже деактивирован")

        except Exception as e:
            parser_logger.exception(
                f"{self.__class__.__name__}: Ошибка на этапе проверки фильтрования поискового запроса: {e}")
        try:
            # Находим и обрабатываем кнопку "Применить"
            primenit_button = self.driver.find_element(By.CSS_SELECTOR, '[class="btn btn-primary"]')
            self.driver.execute_script("arguments[0].click();", primenit_button)
            parser_logger.info(f"{self.__class__.__name__}: Нажпата кнопка 'Применить'")
        except Exception as e:
            parser_logger.exception(
                f"{self.__class__.__name__}: Ошибка на этапе нажатия кнопки 'Применить': {e}")

        try:
            parser_logger.info(f"{self.__class__.__name__}: Ввод запроса '{self.request}' в поисковую строку")

            # Находим поле ввода и вводим запрос
            search_input = self.driver.find_element(By.CSS_SELECTOR, '[id="searchString"]')
            search_input.send_keys(self.request)

            # Нажимаем кнопку поиска
            search_button = self.driver.find_element(By.CSS_SELECTOR, '[class="search__btn"]')
            search_button.click()

            parser_logger.info(f"{self.__class__.__name__}: Поиск по запросу '{self.request}' успешно выполнен")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка на этапе ввода запроса '{self.request}': {e}")




    def _pars_page(self):
        """Парсит карточки на странице Zakupki и сохраняет данные."""
        from src.logger import parser_logger
        parser_logger.info(f"{self.__class__.__name__}: Начало парсинга страницы")

        self.new_data = []
        try:
            # Поиск карточек товаров
            titles = self.driver.find_elements(By.CSS_SELECTOR, '[class="row no-gutters registry-entry__form mr-0"]')
            parser_logger.info(f"{self.__class__.__name__}: Найдено {len(titles)} карточек товаров")
        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка поиска карточек товара: {e}")
            titles = []

        for title in titles:
            try:
                description_element = title.find_element(By.CSS_SELECTOR, '.registry-entry__body-value')
                description = description_element.text
            except Exception:
                description = 'Описание не найдено'

            try:
                url = title.find_element(By.CSS_SELECTOR, '[target="_blank"]').get_attribute('href')
            except Exception:
                url = 'Ссылка не найдена'

            try:
                price = title.find_element(By.CSS_SELECTOR, '[class="price-block__value"]').get_attribute('innerText')
                price = price.replace("&nbsp", "")
            except Exception:
                price = 'Цена не найдена'

            # try:
            #     card_element = title.find_element(By.CSS_SELECTOR, 'a[target="_blank"]')
            #
            #     # Использование JavaScript для получения текста элемента
            #     cards_id = self.driver.execute_script("return arguments[0].textContent;", card_element).strip()
            #
            #     # Проверка, удалось ли получить текст
            #     if not cards_id:
            #         raise ValueError("Текст элемента пустой")
            #
            #     # Логирование успешного получения текста
            #     parser_logger.info(f"{self.__class__.__name__}: Извлечен номер: {cards_id}")
            #
            # except Exception as e:
            #     cards_id = 'Код продукта не найден'
            #     parser_logger.exception(f"{self.__class__.__name__}: Ошибка при извлечении номера: {e}")


            data = {
                'description': description,
                'url': url,
                'price': price,
                # 'cards_ID': cards_id
            }

            # Фильтрация товаров по ключевым словам в `self.items`
            # if any(item.lower() in description.lower() for item in self.items):
            self.new_data.append(data)
            parser_logger.debug(f"{self.__class__.__name__}: Добавлена карточка товара: {data}")

        parser_logger.info(
            f"{self.__class__.__name__}: Парсинг завершён, добавлено {len(self.new_data)} карточек в JSON")


    def _paginator(self):
        """Метод для перелистывания страниц и парсинга карточек."""
        from src.logger import parser_logger
        page_number = 1
        while True:
            try:
                parser_logger.info(f"{self.__class__.__name__}: Парсинг страницы {page_number}.")

                self._load_data()
                parser_logger.info(f"{self.__class__.__name__}: Загружены предыдущие данные (если есть)")

                # Парсинг текущей страницы
                self._pars_page()
                parser_logger.info(
                    f"{self.__class__.__name__}: Парсинг страницы завершён, найдено {len(self.new_data)} товаров")

                self._add_request()
                parser_logger.info(f"{self.__class__.__name__}: Новые данные добавлены в JSON")

                self._save_data()
                parser_logger.info(f"{self.__class__.__name__}: Данные успешно сохранены")

                # self._wait_for_debug()

                # Ожидание, пока кнопка "Следующая страница" станет кликабельной
                wait = WebDriverWait(self.driver, 10)
                next_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.paginator-button.paginator-button-next'))
                )

                # Если кнопка "Следующая страница" найдена, кликаем по ней
                if next_button:
                    parser_logger.info(f"{self.__class__.__name__}: Переход на страницу {page_number + 1}.")
                    self.driver.execute_script("arguments[0].click();", next_button)

                    # Ожидание загрузки новой страницы
                    wait.until(EC.staleness_of(next_button))
                    page_number += 1
                else:
                    parser_logger.info(
                        f"{self.__class__.__name__}: Достигнут конец списка страниц. Пагинация завершена.")
                    break

            except Exception as e:
                parser_logger.exception(f"{self.__class__.__name__}: Ошибка при переходе на следующую страницу: {e}")
                break  # Выход из цикла в случае недоступности кнопки или другой ошибки

    def parse(self):
        """Запускает полный цикл парсинга eBay."""
        from src.logger import parser_logger
        parser_logger.info(f"{self.__class__.__name__}: Начало парсинга Zakupki для запроса '{self.request}'")

        try:
            self._setup()
            parser_logger.info(f"{self.__class__.__name__}: WebDriver успешно настроен")

            self._get_url()
            parser_logger.info(f"{self.__class__.__name__}: Страница eBay успешно загружена")

            self._entering_request()
            parser_logger.info(f"{self.__class__.__name__}: Запрос '{self.request}' отправлен")

            self._paginator()
            parser_logger.info(
                f"{self.__class__.__name__}: Парсинг страницы завершён, найдено {len(self.new_data)} товаров")

            parser_logger.info(
                f"{self.__class__.__name__}: Парсинг завершён, всего обработано {len(self.data)} товаров")

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
#             print(f"\n\033[1;32;4mПарсится сайт eBay\033[0m\n")
#             print(f"\n\033[1;32;4mПоиск артикула: {article}\033[0m\n")
#
#             parser = Zakupki(url='https://zakupki.gov.ru',
#                                request=article,
#                                items=[article, 'Можно добавить что угодно'])
#             parser.parse()
#             parser.clear_terminal()
#         except Exception as e:
#             print('Ошибка при создании объекта парсинга')