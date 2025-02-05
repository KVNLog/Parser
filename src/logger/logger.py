import logging
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self, log_file="parser.log", log_level=logging.DEBUG):
        """Инициализация логгера"""
        self.logger = logging.getLogger("ParserLogger")
        self.logger.setLevel(log_level)

        # Формат логов
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Обработчик для вывода в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        # Обработчик для записи в файл с ротацией
        file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Добавляем обработчики в логгер
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        self.logger.info("Логирование настроено")

    def get_logger(self):
        """Возвращает настроенный логгер"""
        return self.logger

# Создание единственного экземпляра логгера
parser_logger = Logger().get_logger()
