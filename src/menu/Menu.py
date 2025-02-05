import curses


def menu(stdscr):
    curses.curs_set(0)  # Скрыть курсор
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    menu_items = ["Чип и Дип", "eBay", "ETM", "Yandex Market", "[ПАРСИТЬ]", "[ВЫХОД]"]
    selected = [False] * 4  # Храним состояние (галочки)
    current_row = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Добавляем инструкции для пользователя в верхней части экрана
        instructions = [
            "Используйте стрелки ↑ и ↓ для навигации",
            "Нажмите ПРОБЕЛ, чтобы выбрать/отменить парсер",
            "Нажмите ENTER, чтобы подтвердить выбор"
        ]

        for i, instr in enumerate(instructions):
            stdscr.addstr(i + 1, w // 4, instr)  # Выводим инструкции

        for idx, item in enumerate(menu_items):
            x = w // 4  # Отступ слева (можно регулировать)
            y = h // 2 - len(menu_items) // 2 + idx + len(instructions)  # Смещаем вниз после инструкций

            if idx < 4:  # Для парсеров
                checkbox = "[x] " if selected[idx] else "[ ] "
                text = checkbox + item
            else:
                text = item

            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, text)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, text)

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1
        elif key == ord(" "):  # Пробел – переключает галочки
            if current_row < 4:
                selected[current_row] = not selected[current_row]
        elif key == ord("\n"):  # Enter – подтверждение выбора
            if current_row == 4:  # "Парсить"
                return [idx + 1 for idx, checked in enumerate(selected) if checked]
            elif current_row == 5:  # "Выход"
                return []
