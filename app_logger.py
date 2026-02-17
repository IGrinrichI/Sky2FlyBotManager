import os
import re
import sys
from queue import Queue, Empty
from threading import Thread

import frida
import win32process


def resource_path(relative_path) -> str:
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class AppLogger:

    def __init__(self, hwnd: int):
        self.thread_id, self.process_id = win32process.GetWindowThreadProcessId(hwnd)
        # Сигнатуры SWF: FWS (46 57 53), CWS (43 57 53), ZWS (5a 57 53)
        # with open('script.js', 'r', encoding='utf8') as f:
        with open(resource_path('gui_logger_script.js'), 'r', encoding='utf8') as f:
            JS_CODE = f.read()

        self.log_queue = Queue()

        def on_message(message, data):
            if message['type'] == 'send':
                payload = message['payload']
                self.log_queue.put(payload)
                # if payload[0] != '<':
                #     return
                # print(payload)
                return
                # Чистим HTML теги
                clean = re.sub(r'<[^>]*>', '', payload).strip()
                # Фильтр мусора: убираем технические строки и короткие фразы
                if len(clean) > 3 and any(u'а' <= c <= u'я' for c in clean.lower()):
                    # Убираем дублирование из-за особенностей движка Flash
                    print(f"[Sky2Fly]: {clean}")
            # else:
            #     print(message, data)
            # with open('libs_full.txt', 'a', encoding='utf8') as f:
            #     f.write(message['payload'])
            # if message['type'] == 'send' and message['payload']['type'] == 'dump':
            #     with open("extracted.swf", "wb") as f:
            #         f.write(data)
            #     print("[*] Файл сохранен как extracted.swf")

        self.session = frida.attach(self.process_id)
        self.script = self.session.create_script(JS_CODE)
        self.script.on('message', on_message)
        self.script.load()

        self.active_catcher = None
        self.message = Queue()
        # print("Нажми на перелеты")
        # script.exports_sync.startcatching()
        # Thread(target=logger_catcher, daemon=True).start()
        # # time.sleep(3)
        # # script.exports_sync.stopcatching()
        # input("")
        # # input("[?] Нажмите Enter для выхода...")

    def clear_logger(self):
        # Очистка:
        while not self.log_queue.empty():
            try:
                self.log_queue.get_nowait()
            except Empty:
                break

    def clear_message(self):
        # Очистка:
        while not self.message.empty():
            try:
                self.message.get_nowait()
            except Empty:
                break

    def start_catching(self, target='@', min_size=None):
        self.stop_catching()

        self.script.exports_sync.startcatching()

        self.active_catcher = Thread(target=self.logger_catcher, args=(target, min_size), daemon=True)
        self.active_catcher.start()

    def stop_catching(self):
        self.script.exports_sync.stopcatching()
        self.clear_logger()
        self.clear_message()

    def logger_catcher(self, target='@', min_size=None):
        while True:
            message = self.log_queue.get()
            if (min_size is not None and len(message) >= min_size) and re.match(target, message):
                self.stop_catching()
                self.message.put(message)
                break
