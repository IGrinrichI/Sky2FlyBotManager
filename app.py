import shutil
import subprocess

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

import view.clients_widget
import view.presets_widget

import os.path

import requests
from datetime import datetime, timezone


class MainView(BoxLayout):
    executable_url = "https://disk.yandex.ru/d/qGm0xEVx2iIwQA"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if getattr(sys, 'frozen', False):
            Clock.schedule_once(lambda _: setattr(self.ids.update_button, "disabled", not self._check_update()))
            Clock.schedule_interval(lambda _: setattr(self.ids.update_button, "disabled", not self._check_update()), timeout=60)

    def _check_update(self):
        def get_yandex_disk_file_date(public_key):
            # API URL для получения информации о публичном файле
            api_url = 'https://cloud-api.yandex.net/v1/disk/public/resources'

            # Параметры запроса
            params = {
                'public_key': public_key
            }

            # Отправка запроса
            response = requests.get(api_url, params=params)

            if response.status_code == 200:
                data = response.json()
                # Поле 'modified' содержит ISO 8601 дату
                modified_date = data.get('modified')
                return modified_date
            else:
                return f"Ошибка: {response.status_code}, {response.json().get('message')}"

        # --- Использование ---
        public_link = self.executable_url
        try:
            yandex_modify_datetime_utc = datetime.fromisoformat(get_yandex_disk_file_date(public_link)).replace(
                tzinfo=timezone.utc)
        except ValueError:
            return False
        # print(f"Дата изменения на диске: {yandex_modify_datetime_utc}")
        # local_time_zone = datetime.now(timezone.utc).astimezone().tzinfo
        real_modify_datetime_utc = datetime.fromtimestamp(os.path.getmtime(sys.executable), tz=timezone.utc)
        # print(f"Дата изменения локальная: {real_modify_datetime_utc}")
        return yandex_modify_datetime_utc > real_modify_datetime_utc

    def make_hint(self, text):
        hint = Button(text=text)
        Window.add_widget(hint)
        Clock.schedule_once(lambda _: Window.remove_widget(hint), 1)

    def load_update(self):
        try:
            # Запрашиваем прямую ссылку
            api_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download'
            response = requests.get(api_url, params={'public_key': self.executable_url})
            download_url = response.json()['href']
            bat_name = "Sky2FlyBotManagerAutoUpdater.bat"
            shutil.copyfile(resource_path(bat_name),
                            os.path.join(os.path.dirname(sys.executable), bat_name))
            subprocess.Popen(f"start {bat_name} \"{os.path.basename(sys.executable)}\" \"{download_url}\"",
                             shell=True)
            sys.exit(0)
        except Exception:
            self.make_hint("Не удалось скачать обновление, проверьте свое интернет соединение.")


class Sky2FlyBotManagerApp(App):

    def build(self):
        self.icon = resource_path('images/icon.png')
        game = MainView()
        return game


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    import os, sys
    from kivy.resources import resource_add_path, resource_find
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    from kivy.core.window import Window


    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    Window.size = (550, 350)
    Builder.load_file(resource_path("main.kv"))
    Sky2FlyBotManagerApp().run()
