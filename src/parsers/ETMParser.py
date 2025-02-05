import json
import os
import sys

from pandas.core.roperator import rtruediv
from tqdm import tqdm
from time import sleep
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .AbtractParser import AbstractParser
from .AbtractParser import Loading_Source_Data

class ETMParser(AbstractParser):

    def _run_once(self):
        # Проверяем, был ли метод вызван ранее
        if self._is_first_instance():

            # Получение текущей даты и времени
            current_time = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")

            # Формирование пути для файла
            directory = "./data/JSON/ETMData"
            filename = f"ETMData_{current_time}.json"
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
        try:
            self.driver.find_element(By.CSS_SELECTOR, '[class="MuiInputBase-input MuiInputBase-inputAdornedStart mui-style-vnciqk"]').send_keys(self.request)
            # Нажатие кнопки "Ваш город -> ДА"
            self.driver.find_element(By.CSS_SELECTOR, '[class="MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary MuiButton-disableElevation MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary MuiButton-disableElevation tss-1gg6ugo-root-yellow-button mui-style-12bvbwy"]').click()
            # Нажатие кнопки "Использовать куки -> Ок"
            self.driver.find_element(By.CSS_SELECTOR, '[class="MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary MuiButton-disableElevation MuiButton-fullWidth MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary MuiButton-disableElevation MuiButton-fullWidth tss-xu4l57-root-contained mui-style-1l3vhg0"]').click()
            # Нажатие кнопки "Найти"
            self.driver.find_element(By.CSS_SELECTOR, '[class="MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary MuiButton-disableElevation MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary MuiButton-disableElevation tss-9l9isw-root-contained-search_button mui-style-12bvbwy"]').click()
        except Exception as e:
            print('Ошибка на этапе входа на сайт')

    def _pars_page(self):
        self.new_data = []
        # Максимальное количество прокруток (для предотвращения бесконечного цикла)
        max_scrolls = 10
        scroll_count = 0

        #Уменьшаем маштаб отображения страници чтобы уместилось больше карточек
        self.driver.execute_script("document.body.style.zoom='0.5';")

        first_cycle = True
        previous_product_code = ''
        while scroll_count < max_scrolls:
            try:
                titles = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.tss-1n3o4n4-catalog_item.MuiBox-root.mui-style-0'))
                )
            except Exception as e:
                print(f"Ошибка поиска карточек товара")
                break

            for title in titles:
                try:
                    try:
                        description = title.find_element(By.CSS_SELECTOR, '[class="MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineHover tss-lrg5ji-root-blue-title mui-style-i8aqv9"]').get_attribute('innerText')
                    except Exception as e:
                        description = 'Описание не найдено'

                    try:
                        url =  title.find_element(By.CSS_SELECTOR, 'a.MuiTypography-root.MuiTypography-inherit.MuiLink-root.MuiLink-underlineHover').get_attribute('href')
                    except Exception as e:
                        url = 'Ссылка не найдена'

                    try:
                        # Ожидание элемента
                        price = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((
                                By.CSS_SELECTOR,
                                'p[data-testid="catalog-list-item-price-details-0"]'))).text.replace(' ₽/шт', '').replace(' ', '')
                    except Exception as e:
                        price = 'Цена не найдена'

                    try:
                        product_code = title.find_element(By.CSS_SELECTOR, '[class="tss-ao7i46-text MuiBox-root mui-style-0"]').text
                    except Exception as e:
                        product_code = 'Код продукта не найден'

                    try:
                        article = title.find_element(By.CSS_SELECTOR, '[class="tss-9cdrin-good_descr_value"]').text
                    except Exception as e:
                        article = 'Артикул не найден'

                    data = {
                        'description': description,
                        'url': url,
                        'price': price,
                        'product_code': product_code,
                        'article': article
                    }
                    if first_cycle:
                        # if any(item.lower() in description.lower() for item in self.items):
                        self.new_data.append(data)
                        print('Карточка товара добавлена в JSON')
                    else:
                        if not previous_product_code == product_code:
                            self.new_data.append(data)
                            print('Карточка товара добавлена в JSON')


                except Exception as e:
                    print("Ошибка парсинга карточек товара")
                    continue
            try:
                # Прокрутка страницы вниз
                card_height = self.driver.execute_script(
                    "return document.querySelector('.tss-1n3o4n4-catalog_item.MuiBox-root.mui-style-0').offsetHeight;")
                self.driver.execute_script(f"window.scrollBy(0, {card_height});")
                sleep(1)  # Подождать, если контент подгружается

                # Увеличиваем счётчик прокруток
                scroll_count += 1
            except Exception as e:
                print('Ошибка прокрутки')
            previous_product_code = product_code
            first_cycle = False

    def parse(self):
        self._setup()
        self._get_url()
        self._entering_reques()
        self._load_data()
        self._pars_page()
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
#             print(f"\n\033[1;32;4mПарсится сайт ETM\033[0m\n")
#             print(f"\n\033[1;32;4mПоиск артикула: {article}\033[0m\n")
#
#             parser = ETMParser(url='https://www.etm.ru/',
#                                         request=article,
#                                         items=[article, 'Можно добавить что угодно'])
#             parser.parse()
#             parser.clear_terminal()
#         except Exception as e:
#             print('Ошибка при создании объекта парсинга')
