from abc import ABC, abstractmethod
import os
import sys
import json
import pandas as pd
from time import sleep
from datetime import datetime
import subprocess

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.bidi.cdp import logger




class AbstractParser(ABC):
    _first_instance_called = {}

    _filepath = ""

    def __init__(self, url, request, items=[], version_chrome=None, telegram_sender=None):
        """
        Инициализатор парсера.

        :param url: URL для парсинга
        :param request: Запрос для поиска
        :param items: Дополнительные параметры
        :param version_chrome: Версия Chrome (если используется Selenium)
        :param telegram_sender: Объект отправки уведомлений в Telegram (если используется)
        """
        from src.logger import parser_logger
        try:
            self.url = url
            self.request = request
            self.items = items
            self.version_chrome = version_chrome
            self.data = []
            self.telegram_sender = telegram_sender

            # Определяем имя класса
            _class_name = self.__class__.__name__

            # Проверяем, первый ли это вызов данного класса
            if _class_name not in AbstractParser._first_instance_called:
                AbstractParser._first_instance_called[_class_name] = True
                parser_logger.info(f"Первый вызов класса {self.__class__.__name__}")
            else:
                AbstractParser._first_instance_called[_class_name] = False
                parser_logger.warning(f"Повторный вызов класса {self.__class__.__name__}, _run_once() не будет запущен")

            # Вызываем _run_once(), если это первый экземпляр
            self._run_once()

            parser_logger.info(
                f"Экземпляр парсера {self.__class__.__name__} успешно создан: URL={self.url}, Request={self.request}")

        except Exception as e:
            parser_logger.exception(f"Ошибка при инициализации {self.__class__.__name__}: {e}")

    def _is_first_instance(self):
        """ Проверяет, является ли этот объект первым экземпляром класса. """
        return AbstractParser._first_instance_called[self.__class__.__name__]

    def _setup(self):
        """Настраивает и запускает Chrome WebDriver"""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Настройка Chrome WebDriver")

            # Создание объекта настроек Chrome
            chrome_options = Options()
            chrome_options.page_load_strategy = 'eager'  # Загружать страницу быстрее

            # Оптимизация запуска браузера (можно включить при необходимости)
            # chrome_options.add_argument("--disable-extensions")  # Отключает расширения
            # chrome_options.add_argument("--disable-gpu")  # Отключает использование GPU (важно для headless)
            # chrome_options.add_argument("--no-sandbox")  # Отключает режим песочницы (ускоряет запуск)

            # Запуск Chrome
            parser_logger.info(f"{self.__class__.__name__}: Запуск Chrome WebDriver (headless=False)")
            self.driver = uc.Chrome(options=chrome_options, headless=False, use_subprocess=False,
                                    version_main=self.version_chrome)

            parser_logger.info(f"{self.__class__.__name__}: Chrome WebDriver успешно запущен")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при запуске Chrome WebDriver: {e}")

    def _get_url(self):
        """Загружает страницу в Chrome WebDriver"""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Открытие URL {self.url}")

            # Переход по указанному URL
            self.driver.get(self.url)

            parser_logger.info(f"{self.__class__.__name__}: Успешно загружен URL {self.url}")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при загрузке URL {self.url}: {e}")

    @abstractmethod
    def _run_once(self):
        pass

    @abstractmethod
    def _entering_request(self):
        pass

    @abstractmethod
    def _pars_page(self):
        pass

    def _add_request(self):
        """Добавляет новые данные в self.data, связывая их с текущим запросом."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Добавление данных для запроса {self.request}")

            # Проверка, есть ли новые данные
            if not hasattr(self, 'new_data') or not self.new_data:
                parser_logger.warning(f"{self.__class__.__name__}: new_data пуст или отсутствует, данные не добавлены")
                return

            for data in self.new_data:
                new_data = {self.request: data}
                self.data.append(new_data)

            parser_logger.info(f"{self.__class__.__name__}: Добавлено {len(self.new_data)} записей в self.data")

        except Exception as e:
            parser_logger.exception(
                f"{self.__class__.__name__}: Ошибка при добавлении данных для запроса {self.request}: {e}")

    def _load_data(self):
        """Загружает данные из JSON-файла в self.data."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Загрузка данных из файла {AbstractParser._filepath}")

            # Чтение файла
            with open(AbstractParser._filepath, 'r', encoding='utf-8') as file:
                file_data = json.load(file)

            # Извлечение данных (игнорирование метаинформации)
            self.data = file_data.get("Данные", [])

            parser_logger.info(f"{self.__class__.__name__}: Успешно загружено {len(self.data)} записей из JSON")

        except FileNotFoundError:
            parser_logger.error(
                f"{self.__class__.__name__}: Файл {AbstractParser._filepath} не найден, загрузка данных невозможна")
            self.data = []
        except json.JSONDecodeError as e:
            parser_logger.error(
                f"{self.__class__.__name__}: Ошибка декодирования JSON в {AbstractParser._filepath}: {e}")
            self.data = []
        except Exception as e:
            parser_logger.exception(
                f"{self.__class__.__name__}: Ошибка при загрузке данных из {AbstractParser._filepath}: {e}")
            self.data = []

    def _save_data(self):
        """Сохраняет данные в JSON-файл, обновляя или создавая его."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Сохранение данных в файл {AbstractParser._filepath}")

            # Попытка загрузить существующий файл, чтобы сохранить метаинформацию
            try:
                with open(AbstractParser._filepath, 'r', encoding='utf-8') as file:
                    file_data = json.load(file)

                # Обновляем только поле "Данные"
                file_data["Данные"] = self.data
                parser_logger.info(f"{self.__class__.__name__}: Файл найден, обновляем данные")

            except (json.JSONDecodeError, FileNotFoundError):
                # Если файл отсутствует или повреждён, создаем новую структуру
                parser_logger.warning(f"{self.__class__.__name__}: Файл отсутствует или повреждён, создаем новый")
                file_data = {
                    "Дата и время создания файла": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "Данные": self.data
                }

            # Сохраняем обновленные данные в файл
            with open(AbstractParser._filepath, 'w', encoding='utf-8') as file:
                json.dump(file_data, file, ensure_ascii=False, indent=4)

            parser_logger.info(
                f"{self.__class__.__name__}: Данные успешно сохранены в {AbstractParser._filepath}, записано {len(self.data)} записей")

        except Exception as e:
            parser_logger.exception(
                f"{self.__class__.__name__}: Ошибка при сохранении данных в {AbstractParser._filepath}: {e}")

    def _wait_for_debug(self):
        """Ожидает нажатие клавиши '8' для продолжения работы."""
        from src.logger import parser_logger
        try:
            parser_logger.info(
                f"{self.__class__.__name__}: Включен режим ожидания отладки (нажмите '8' для продолжения)")
            print("Ожидание нажатия клавиши '8' для продолжения...")

            while True:
                user_input = input("Введите '8' чтобы продолжить: ")
                parser_logger.debug(f"{self.__class__.__name__}: Введено '{user_input}'")

                if user_input == "8":
                    parser_logger.info(f"{self.__class__.__name__}: Ввод подтверждён, продолжаем выполнение")
                    break

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка во время ожидания отладки: {e}")


    @staticmethod
    def clear_terminal():
        """Очищает терминал в Windows, Linux, macOS и поддерживает PyCharm/VSCode."""
        from src.logger import parser_logger
        try:
            parser_logger.info("Очистка терминала запущена")

            # Определяем ОС
            os_type = "Windows" if os.name == 'nt' else "Linux/macOS"
            parser_logger.debug(f"Операционная система: {os_type}")

            # Альтернативная очистка (работает в PyCharm/VSCode)
            print("\n" * 100)

            # Основной способ очистки экрана
            if os.name == 'nt':  # Windows
                os.system('cls')
            else:  # Linux / macOS
                os.system('clear')

            # Альтернативный метод (ANSI-коды, работает в PyCharm и VSCode)
            sys.stdout.write("\033c")  # Полная очистка ANSI
            sys.stdout.write("\033[H\033[J")  # Очистка и перемещение курсора в начало
            sys.stdout.flush()

            # Запасной метод (гарантированно работает в терминале Windows)
            if os.name == 'nt':
                subprocess.run("cls", shell=True, check=True)
            else:
                subprocess.run("clear", shell=True, check=True)

            # Короткая пауза для корректного обновления экрана
            sleep(0.05)

            parser_logger.info("Очистка терминала выполнена успешно")

        except Exception as e:
            parser_logger.exception(f"Ошибка очистки терминала: {e}")

    def __del__(self):
        """Закрывает WebDriver при удалении объекта."""
        from src.logger import parser_logger
        try:
            if hasattr(self, "driver") and self.driver is not None:
                parser_logger.info(f"{self.__class__.__name__}: Завершение WebDriver")
                self.driver.quit()
                parser_logger.info(f"{self.__class__.__name__}: WebDriver успешно завершён")
            else:
                parser_logger.warning(f"{self.__class__.__name__}: WebDriver уже был закрыт или не инициализирован")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при завершении WebDriver: {e}")




class Loading_Source_Data:
    def __init__(self, file_path):
        """
        Класс для загрузки артикулов из Excel-файла.

        :param file_path: Путь к Excel-файлу.
        """
        from src.logger import parser_logger
        self.file_path = file_path
        parser_logger.info(f"Инициализирован загрузчик данных, файл: {self.file_path}")

    def loading_articles(self):
        """Загружает артикулы из первого столбца Excel-файла."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"Загрузка артикулов из файла: {self.file_path}")

            # Читаем Excel
            articles = pd.read_excel(self.file_path, sheet_name=0, usecols=[0], header=None)
            articles_list = articles.iloc[:, 0].dropna().astype(str).tolist()

            parser_logger.info(f"Успешно загружено {len(articles_list)} артикулов из {self.file_path}")
            return articles_list

        except FileNotFoundError:
            parser_logger.error(f"Файл {self.file_path} не найден, загрузка невозможна")
            return []
        except pd.errors.EmptyDataError:
            parser_logger.error(f"Файл {self.file_path} пуст, данные не загружены")
            return []
        except Exception as e:
            parser_logger.exception(f"Ошибка при загрузке артикулов из {self.file_path}: {e}")
            return []

