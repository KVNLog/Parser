import sys
import time
import curses
from tqdm import tqdm
from src import (
    menu, CipDipParser, eBayParser, ETMParser, YandexMarketParser,
    ExcelSaver, AbstractParser, Loading_Source_Data, parser_logger
)


def main():
    """Главная функция запуска парсеров"""
    parser_logger.info("Программа парсинга запущена")

    selected_parsers = curses.wrapper(menu)

    if selected_parsers:
        parser_logger.info(f"Выбраны парсеры: {selected_parsers}")
        print(f"Выбраны парсеры: {selected_parsers}")

        for parser_id in selected_parsers:
            try:
                if parser_id == 1:
                    site_name = "Чип и Дип"
                    parser_class = CipDipParser
                    json_folder = "data/JSON/ChipDipData"
                elif parser_id == 2:
                    site_name = "eBay"
                    parser_class = eBayParser
                    json_folder = "data/JSON/eBayData"
                elif parser_id == 3:
                    site_name = "ETM"
                    parser_class = ETMParser
                    json_folder = "data/JSON/ETMData"
                elif parser_id == 4:
                    site_name = "Yandex Market"
                    parser_class = YandexMarketParser
                    json_folder = "data/JSON/YandexMarketData"
                else:
                    parser_logger.warning(f"Неизвестный ID парсера: {parser_id}")
                    continue

                parser_logger.info(f"Запуск парсера: {site_name}")
                print(f"\nЗапущен парсер: {site_name}")

                # Загружаем артикулы из Excel
                articles = list(Loading_Source_Data('Рабочий.xlsx').loading_articles())
                parser_logger.info(f"Загружено {len(articles)} артикулов для парсинга")

                # Очищаем терминал перед парсингом
                AbstractParser.clear_terminal()

                # Прогресс-бар
                progress_bar = tqdm(articles, desc=f"Обработка {site_name}", unit="шт", ncols=80, ascii=True)

                # Парсинг по каждому артикулу
                for article in progress_bar:
                    try:
                        sys.stdout.flush()
                        parser_logger.info(f"Поиск артикула {article} на сайте {site_name}")

                        print(f"\n\033[1;32;4mПарсится сайт {site_name}\033[0m\n")
                        print(f"\n\033[1;32;4mПоиск артикула: {article}\033[0m\n")

                        parser = parser_class(url=f"https://www.{site_name.lower().replace(' ', '')}.com/",
                                              request=article,
                                              items=[article, 'Можно добавить что угодно'])
                        parser.parse()
                        parser.clear_terminal()
                        parser_logger.info(f"Артикул {article} успешно обработан")
                    except Exception as e:
                        parser_logger.exception(f"Ошибка при парсинге артикула {article} на {site_name}: {e}")

                # Сохранение данных в Excel
                try:
                    saver = ExcelSaver(json_folder=json_folder)
                    saver.process_data()
                    parser_logger.info(f"Данные успешно сохранены в {json_folder}")
                except Exception as e:
                    parser_logger.exception(f"Ошибка при сохранении данных в {json_folder}: {e}")

            except Exception as e:
                parser_logger.exception(f"Ошибка в процессе парсинга {site_name}: {e}")

        # Объединение всех данных в один Excel
        try:
            saver_aggregate = ExcelSaver()
            saver_aggregate.aggregate_prices_to_first_sheet()
            parser_logger.info("Все данные успешно объединены в Excel")
        except Exception as e:
            parser_logger.exception(f"Ошибка при объединении данных в Excel: {e}")

    else:
        parser_logger.warning("Выход без выбора парсеров")
        print("Выход без выбора парсеров.")

    time.sleep(5)  # Пауза перед выходом
    parser_logger.info("Завершение программы")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        parser_logger.critical(f"Критическая ошибка программы: {e}", exc_info=True)
    input("Нажмите Enter для выхода...")
