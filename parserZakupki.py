import sys
import time
import curses
from tqdm import tqdm
from src import (
    menu, CipDipParser, eBayParser, ETMParser, YandexMarketParser,
    ExcelSaver, AbstractParser, Loading_Source_Data, parser_logger, Zakupki, ExcelSaverZakupki
)

if __name__ == '__main__':
    articles = list(Loading_Source_Data('Рабочий.xlsx').loading_articles())
    AbstractParser.clear_terminal()
    progress_bar = tqdm(articles, desc="Обработка артикулов", unit="шт", ncols=80, ascii=True)

    for article in progress_bar:
        try:
            sys.stdout.flush()  # Принудительное обновление потока (важно для PyCharm!)
            print(f"\n\033[1;32;4mПарсится сайт eBay\033[0m\n")
            print(f"\n\033[1;32;4mПоиск артикула: {article}\033[0m\n")

            parser = Zakupki(url='https://zakupki.gov.ru',
                             request=article,
                             items=[article, 'Можно добавить что угодно'])
            parser.parse()
            parser.clear_terminal()
        except Exception as e:
            print('Ошибка при создании объекта парсинга')

    # Сохранение данных в Excel
    json_folder = "data/JSON/Zakupki"
    try:
        saver = ExcelSaverZakupki(json_folder=json_folder)
        saver.process_data()
        parser_logger.info(f"Данные успешно сохранены в {json_folder}")
    except Exception as e:
        parser_logger.exception(f"Ошибка при сохранении данных в {json_folder}: {e}")