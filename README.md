# 🛒 Multi-Site Web Scraper

**Multi-Site Web Scraper** — это мощный парсер, который автоматически собирает информацию о товарах с различных маркетплейсов, включая Яндекс.Маркет, eBay, ChipDip и ETM. Поддерживает логирование, обработку ошибок и сохранение данных в JSON и Excel.

## 📌 Функции
- ✅ **Парсинг товаров** с разных сайтов по артикулу.
- ✅ **Сбор данных**: название, цена, ссылка, ID карточки.
- ✅ **Поддержка нескольких маркетплейсов** (YandexMarket, eBay, ETM, ChipDip).
- ✅ **Автоматическое сохранение** в JSON и Excel.
- ✅ **Логирование**: ротация логов, отладочные и критические сообщения.
- ✅ **Обработка ошибок** с исключениями.
- ✅ **Гибкая структура кода** с возможностью расширения.
- ✅ **Упрощённый запуск через batch-скрипт** (приоритетный способ).

---

## 🚀 Установка

### **1️⃣ Запуск через batch-скрипт (рекомендуемый способ)**
1️⃣ **Клонируйте репозиторий** или **скачайте архив с кодом** с GitHub:
- Для клонирования:
```sh
git clone https://github.com/your-username/MultiSiteScraper.git
cd MultiSiteScraper
```
- Для скачивания архива: зайдите на страницу репозитория, нажмите кнопку "Code" → "Download ZIP" и распакуйте архив.

2️⃣ **Запустите файл** `parser.bat` (Windows):
```sh
parser.bat
```
3️⃣ Скрипт автоматически:
- Создаст виртуальное окружение (если его нет).
- Установит зависимости из `requirements.txt`.
- Запустит программу `parser.py`.

### **2️⃣ Ручная установка и запуск**
#### **Клонирование репозитория**
```sh
git clone https://github.com/your-username/MultiSiteScraper.git
cd MultiSiteScraper
```
#### **Установка зависимостей**
Создайте виртуальное окружение (по желанию) и установите библиотеки:
```sh
pip install -r requirements.txt
```
#### **Запуск**
```sh
python src/parser.py
```

---

## 📂 Структура проекта
```
Parser/
│── data/                     # Данные парсинга
│   │── JSON/                 # JSON-файлы с результатами
│   │   │── ChipDipData       # Данные с ChipDip
│   │   │── eBayData          # Данные с eBay
│   │   │── ETMData           # Данные с ETM
│   │   │── YandexMarketData  # Данные с Яндекс.Маркета
│── src/                      # Исходный код
│   │── logger/               # Логирование
│   │   │── logger.py         # Настройка логов
│   │── menu/                 # Меню выбора
│   │   │── Menu.py           # Логика меню
│   │── parsers/              # Парсеры для маркетплейсов
│   │   │── AbstractParser.py # Базовый класс парсера
│   │   │── ChipDipParser.py  # Парсер ChipDip
│   │   │── eBayParser.py     # Парсер eBay
│   │   │── ETMParser.py      # Парсер ETM
│   │   │── YandexMarketParser.py # Парсер Яндекс.Маркета
│   │── utilities/            # Утилиты
│   │   │── ExcelSaver.py     # Сохранение данных в Excel
│── requirements.txt          # Зависимости проекта
│── Рабочий.xlsx              # Excel с артикулами
│── parser.log                # Лог-файл
│── parser.bat                # Batch-скрипт для автоматического запуска
│── README.md                 # Документация проекта
```

---

## 📊 Логирование
Программа ведёт **подробное логирование**:
- Все логи пишутся в **parser.log**.
- Лог-файл **ротуируется** (ограничение по размеру, хранение нескольких копий).
- В консоль выводятся только **важные сообщения**.

Пример логов:
```
2025-02-05 15:20:01 - INFO - MultiSiteScraper: Программа парсинга запущена
2025-02-05 15:20:02 - INFO - MultiSiteScraper: Выбраны парсеры: [1, 3]
2025-02-05 15:20:06 - INFO - MultiSiteScraper: Загружено 50 артикулов для парсинга
2025-02-05 15:20:09 - INFO - MultiSiteScraper: Данные успешно сохранены в data/JSON/YandexMarketData
```

---

## 🤝 Контрибьютинг
Если у вас есть предложения по улучшению — **форкните репозиторий** и создайте pull request! 🚀

---

## 📜 Лицензия
Этот проект распространяется под лицензией **MIT**. Вы можете использовать и модифицировать код без ограничений. 😊
