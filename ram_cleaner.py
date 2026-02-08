import ctypes
import time

# Загружаем необходимые библиотеки Windows
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

# Константы прав доступа для открытия процесса
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_SET_QUOTA = 0x0100

import win32process


def clear_process_ram(pid=None, hwnd=None):
    if hwnd:
        thread_id, pid = win32process.GetWindowThreadProcessId(hwnd)
    elif pid is None:
        print("Не задан процесс для очистки памяти.")
        return False

    # 1. Открываем процесс с нужными правами
    handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, pid)

    if not handle:
        print(f"Ошибка: Не удалось открыть процесс {pid}. Проверьте права (запуск от админа?).")
        return False

    try:
        # 2. Вызываем EmptyWorkingSet для сброса страниц памяти в своп
        result = psapi.EmptyWorkingSet(handle)
        if result:
            print(f"RAM процесса {pid} успешно 'очищена' (перемещена в файл подкачки).")
            return True
        else:
            print(f"Не удалось очистить память. Код ошибки: {kernel32.GetLastError()}")
            return False
    finally:
        # 3. Всегда закрываем дескриптор процесса
        kernel32.CloseHandle(handle)


def start_ram_cleaner(hwnd, max_ram=300):
    from threading import Thread
    import psutil

    thread_id, pid = win32process.GetWindowThreadProcessId(hwnd)

    try:
        process = psutil.Process(pid)
        mem_info = process.memory_info()

        # # Конвертируем байты в мегабайты для удобства
        # rss_mb = mem_info.rss / (1024 * 1024)
        # vms_mb = mem_info.vms / (1024 * 1024)

        # print(f"Процесс [PID: {pid}]")
        # print(f"Используемая RAM (RSS): {rss_mb:.2f} MB")
        # print(f"Виртуальная память (VMS): {vms_mb:.2f} MB")
        #
        # return rss_mb
    except psutil.NoSuchProcess:
        print("Ошибка: Процесс не найден.")
    except psutil.AccessDenied:
        print("Ошибка: Недостаточно прав для доступа к данным процесса.")

    def check_clean():
        while True:
            if process.memory_info().rss / (1024 * 1024) > max_ram:
                clear_process_ram(pid=pid)
            time.sleep(30)

    Thread(target=check_clean, daemon=True).start()
