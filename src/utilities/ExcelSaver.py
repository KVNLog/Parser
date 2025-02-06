import json
import os
import pandas as pd
from openpyxl import load_workbook, Workbook


class ExcelSaver:
    def __init__(self, excel_file="Рабочий.xlsx", json_folder="json_data"):
        """Инициализирует объект для работы с Excel и JSON-данными."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Инициализация класса")

            self.excel_file = excel_file  # Фиксированный путь к Excel-файлу
            self.json_folder = json_folder
            self.df = None  # DataFrame для работы с Excel
            self.workbook = None  # Workbook для работы с несколькими листами
            self.articles = []  # Список артикулов из первого столбца

            parser_logger.debug(
                f"{self.__class__.__name__}: Экземпляр создан с excel_file='{self.excel_file}', json_folder='{self.json_folder}'")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при инициализации класса: {e}")

    import os

    def _get_latest_json(self, folder):
        """Находит самый свежий JSON-файл в указанной папке."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Поиск самого свежего JSON-файла в папке '{folder}'")

            # Получаем список JSON-файлов
            json_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".json")]
            parser_logger.debug(f"{self.__class__.__name__}: Найдено {len(json_files)} JSON-файлов: {json_files}")

            # Если файлов нет — выдаем предупреждение и исключение
            if not json_files:
                parser_logger.warning(
                    f"{self.__class__.__name__}: Нет JSON-файлов в папке '{folder}', поиск невозможен")
                raise FileNotFoundError("Нет JSON-файлов в указанной папке.")

            # Определяем самый свежий файл
            latest_file = max(json_files, key=os.path.getmtime)
            parser_logger.info(f"{self.__class__.__name__}: Выбран самый свежий JSON-файл: '{latest_file}'")

            return latest_file

        except FileNotFoundError:
            parser_logger.warning(f"{self.__class__.__name__}: Ошибка: Папка '{folder}' не найдена или пустая")
            raise

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при поиске JSON-файлов в '{folder}': {e}")
            raise

    def _load_price_from_json(self):
        """Загружает данные из JSON-файла."""
        from src.logger import parser_logger
        try:
            self.json_file = self._get_latest_json(self.json_folder)  # Выбираем самый свежий JSON-файл
            parser_logger.info(f"{self.__class__.__name__}: Начало загрузки данных из {self.json_file}")

            # Читаем JSON
            with open(self.json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)

            parser_logger.info(
                f"{self.__class__.__name__}: Данные из {self.json_file} успешно загружены ({len(data)} записей)")
            return data

        except FileNotFoundError:
            parser_logger.warning(
                f"{self.__class__.__name__}: Файл JSON не найден ({self.json_file}), данные не загружены")
            return {}

        except json.JSONDecodeError as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при разборе JSON-файла {self.json_file}: {e}")
            return {}

    def _open_excel(self):
        """Открывает существующий Excel-файл и загружает артикулы с первого листа."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Открытие Excel-файла '{self.excel_file}'")

            # Загружаем книгу
            self.workbook = load_workbook(self.excel_file)
            sheet_name = self.workbook.sheetnames[0]  # Первый лист
            parser_logger.debug(f"{self.__class__.__name__}: Загружается лист '{sheet_name}'")

            # Загружаем DataFrame
            self.df = pd.read_excel(self.excel_file, sheet_name=sheet_name, engine='openpyxl', header=None)

            # Извлекаем артикулы
            self.articles = self.df.iloc[:, 0].dropna().astype(str).tolist()
            parser_logger.info(
                f"{self.__class__.__name__}: Excel-файл загружен, считано {len(self.articles)} артикулов")

        except FileNotFoundError:
            parser_logger.warning(f"{self.__class__.__name__}: Файл '{self.excel_file}' не найден, процесс остановлен")
            raise  # Останавливаем выполнение

        except Exception as e:
            parser_logger.exception(
                f"{self.__class__.__name__}: Ошибка при загрузке Excel-файла '{self.excel_file}': {e}")
            raise

    def _create_json_sheet(self):
        """Создаёт новый лист с именем JSON-файла и записывает данные по артикулам."""
        from src.logger import parser_logger
        try:
            # Получаем последний JSON-файл
            self.json_file = self._get_latest_json(self.json_folder)
            parser_logger.info(f"{self.__class__.__name__}: Создание нового листа из JSON-файла '{self.json_file}'")

            # Загружаем данные из JSON
            self.data = self._load_price_from_json()

            # Определяем имя нового листа
            sheet_name = os.path.basename(self.json_file).split('.')[0].split("_")[0]
            parser_logger.debug(f"{self.__class__.__name__}: Имя нового листа: {sheet_name}")

            # Если лист уже существует — удаляем его
            if sheet_name in self.workbook.sheetnames:
                parser_logger.warning(f"{self.__class__.__name__}: Лист '{sheet_name}' уже существует, удаляем его")
                self.workbook.remove(self.workbook[sheet_name])

            # Создаём новый лист
            self.workbook.create_sheet(sheet_name)
            ws = self.workbook[sheet_name]

            # Записываем заголовки (можно раскомментировать, если нужны заголовки)
            # ws.append(["Артикул", "Цена 1", "Цена 2", "Цена 3", "..."])

            count_written = 0  # Считаем, сколько артикулов записано
            for article in self.articles:
                prices = []
                for item in self.data.get("Данные", []):
                    if article in item:
                        price = item[article].get("price")
                        prices.append(price)

                if prices:
                    ws.append([article] + prices)
                    count_written += 1
                else:
                    ws.append([article, "Не найдено"])
                    parser_logger.debug(f"{self.__class__.__name__}: Для артикула '{article}' данные не найдены")

            parser_logger.info(
                f"{self.__class__.__name__}: Создан новый лист '{sheet_name}', записано {count_written} артикулов")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при создании листа '{sheet_name}': {e}")

    def _save_to_excel(self):
        """Сохраняет изменения в Excel-файл."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Сохранение изменений в '{self.excel_file}'")

            self.workbook.save(self.excel_file)

            parser_logger.info(f"{self.__class__.__name__}: Изменения успешно сохранены в '{self.excel_file}'")

        except PermissionError:
            parser_logger.exception(
                f"{self.__class__.__name__}: Ошибка: Файл '{self.excel_file}' открыт в другой программе, сохранение невозможно")
        except Exception as e:
            parser_logger.exception(
                f"{self.__class__.__name__}: Ошибка при сохранении в Excel-файл '{self.excel_file}': {e}")

    def process_data(self):
        """Выполняет полный цикл обработки данных: загрузка, обновление и сохранение."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Начало обработки данных")

            self._open_excel()
            parser_logger.info(f"{self.__class__.__name__}: Excel-файл успешно загружен")

            self._create_json_sheet()
            parser_logger.info(f"{self.__class__.__name__}: Новый лист с JSON-данными успешно создан")

            self._save_to_excel()
            parser_logger.info(f"{self.__class__.__name__}: Изменения сохранены в Excel-файл")

            parser_logger.info(f"{self.__class__.__name__}: Обработка данных завершена")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка во время обработки данных: {e}")

    def aggregate_prices_to_first_sheet(self):
        """Собирает все цены с каждого листа и аккумулирует их на первом листе."""
        from src.logger import parser_logger
        try:
            parser_logger.info(f"{self.__class__.__name__}: Начало агрегации цен в Excel-файл '{self.excel_file}'")

            # Открываем Excel
            self._open_excel()
            first_sheet_name = self.workbook.sheetnames[0]
            first_sheet = self.workbook[first_sheet_name]
            parser_logger.debug(f"{self.__class__.__name__}: Первый лист для агрегации: '{first_sheet_name}'")

            # Словарь для аккумулирования цен по артикулам
            aggregated_data = {article: [] for article in self.articles}

            # Обход всех листов, кроме первого
            for sheet_name in self.workbook.sheetnames[1:]:
                sheet = self.workbook[sheet_name]
                parser_logger.info(f"{self.__class__.__name__}: Обрабатываем лист '{sheet_name}'")

                for row in sheet.iter_rows(min_row=1, values_only=True):
                    article = row[0]
                    prices = row[1:]

                    if article in aggregated_data:
                        aggregated_data[article].extend([price for price in prices if price])
                    else:
                        parser_logger.debug(
                            f"{self.__class__.__name__}: Артикул '{article}' не найден в основном списке")

            # Очистка первой страницы от старых данных
            first_sheet.delete_rows(1, first_sheet.max_row)

            # Запись данных на первый лист
            count_written = 0
            for article, prices in aggregated_data.items():
                first_sheet.append([article] + prices)
                count_written += 1

            parser_logger.info(f"{self.__class__.__name__}: На первый лист записано {count_written} артикулов")

            # Сохранение изменений
            self._save_to_excel()
            parser_logger.info(
                f"{self.__class__.__name__}: Агрегация завершена, данные сохранены в '{self.excel_file}'")

        except Exception as e:
            parser_logger.exception(f"{self.__class__.__name__}: Ошибка при агрегации цен: {e}")

# # Пример использования
# saver = ExcelSaver(json_folder="JSON/ChipDipData")
# saver1 = ExcelSaver(json_folder="JSON/eBayData")
# saver2 = ExcelSaver(json_folder="JSON/ETMData")
# saver3 = ExcelSaver(json_folder="JSON/YandexMarketData")
# saver.process_data()
# saver1.process_data()
# saver2.process_data()
# saver3.process_data()
# saver3.aggregate_prices_to_first_sheet()
