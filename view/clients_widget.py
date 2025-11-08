import os
import sys
import time

import cv2
import numpy as np
import psutil
import win32clipboard
import win32gui
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

from farm_process import get_farm_process
from licence import get_trial_time
from screen_capture import CaptureWindow


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ClientButton(BoxLayout):
    def __init__(self, hwnd, **kwargs):
        super().__init__(**kwargs)
        height = 32
        self.size_hint_y = None
        self.height = height
        self.hwnd = hwnd
        self.miniature = None
        self.process = None
        self.stdout = None
        self.log_text = ''

        self.layout = BoxLayout(orientation='horizontal')
        self.layout.pos = self.pos
        self.bind(
            pos=lambda obj, pos: setattr(self.layout, 'pos', pos),
            size=lambda obj, size: setattr(self.layout, 'size', size)
        )
        self.add_widget(self.layout)

        # Вставляем миниатюру персонажа
        self.set_miniature()

        self.start_button = Button(
            size_hint=(None, None),
            size=(height, height),
            background_normal=resource_path('images/play_icon.png')
        )
        self.start_button.bind(on_release=self.start_event)
        self.layout.add_widget(self.start_button)

        self.stop_button = Button(
            size_hint=(None, None),
            size=(height, height),
            background_normal=resource_path('images/stop_icon.png')
        )
        self.stop_button.bind(on_release=self.stop_event)
        self.layout.add_widget(self.stop_button)

        self.pause_button = Button(
            size_hint=(None, None),
            size=(height, height),
            background_normal=resource_path('images/pause_icon.png')
        )
        self.pause_button.bind(on_release=self.pause_event)

        self.resume_button = Button(
            size_hint=(None, None),
            size=(height, height),
            background_normal=resource_path('images/resume_icon.png')
        )
        self.resume_button.bind(on_release=self.resume_event)

        self.log_button = Button(
            size_hint=(None, None),
            size=(height, height),
            background_normal=resource_path('images/log_icon.png')
        )
        self.log_button.bind(on_release=self.log_event)
        self.layout.add_widget(self.log_button)

        def process_alive_checker(_):
            if self.process is not None and not self.process.is_alive():
                self.stop_event()

        Clock.schedule_interval(process_alive_checker, timeout=1)

        def stdout_reader(_):
            while self.process is not None and self.stdout.poll():
                self.log_text = self.log_text + self.stdout.recv()

        Clock.schedule_interval(stdout_reader, timeout=1)

    def set_miniature(self):
        self.miniature = BoxLayout(size_hint=(None, None), size=(self.height, self.height))
        self.miniature.pos = self.pos
        self.layout.add_widget(self.miniature)
        self.update_miniature()

    def update_miniature(self):
        total_offset = 1
        image = CaptureWindow(hwnd=self.hwnd, to_rgb=False, window=(total_offset, total_offset, 40, 40))
        if all(image[2, 2] != [143, 147, 153]):
            offset_color = [119, 104, 83]
            offset_x = 0
            for offset_x in range(40):
                if all(image[0, offset_x] != offset_color):
                    break
            total_offset = 8
            image = CaptureWindow(hwnd=self.hwnd, to_rgb=False,
                                  window=(offset_x + total_offset, total_offset, 72 + offset_x, 72))
        image = cv2.resize(image, (self.height, self.height))
        w, h, _ = image.shape
        texture = Texture.create(size=(w, h))
        texture.blit_buffer(np.flipud(image).flatten(), colorfmt='bgr', bufferfmt='ubyte')
        self.miniature.clear_widgets()
        self.miniature.add_widget(Image(size_hint=(None, None), size=(w, h), texture=texture))

    def start_event(self, *args, **kwargs):
        app = App.get_running_app().root

        if getattr(sys, 'frozen', False):
            if not os.path.exists('key'):
                app.make_hint('Отсутствует ключ доступа, обратитесь к разработчику.')
                return

            with open('key', 'rb') as f:
                hash_key = f.read()
            trial_time = get_trial_time(hash_key)
            if trial_time <= time.time():
                app.make_hint('Триал окончен, обратитесь к разработчику ;)')
                return
        else:
            trial_time = 99999999999999999

        selected_preset = app.ids.presets_widget.selected_preset
        if selected_preset is not None:
            if hasattr(sys, '_MEIPASS'):
                preset = selected_preset.text + '.preset'
            else:
                preset = os.path.join('presets', selected_preset.text + '.preset')

            process, stdout = get_farm_process(hwnd=self.hwnd, preset=preset, trial_time=trial_time)
            process.start()
            self.process = process
            self.stdout = stdout
            self.log_text = ''

            self.layout.clear_widgets()
            self.layout.add_widget(self.miniature)
            self.layout.add_widget(self.pause_button)
            self.layout.add_widget(self.stop_button)
            self.layout.add_widget(self.log_button)

    def stop_event(self, *args, **kwargs):
        if self.process is not None:
            self.process.terminate()
            self.process = None
            try:
                while self.stdout.poll():
                    self.log_text = self.log_text + self.stdout.recv()
            except BrokenPipeError:
                pass
            self.stdout.close()

            self.layout.clear_widgets()
            self.layout.add_widget(self.miniature)
            self.layout.add_widget(self.start_button)
            self.layout.add_widget(self.stop_button)
            self.layout.add_widget(self.log_button)

    def pause_event(self, *args, **kwargs):
        if self.process is not None:
            psutil.Process(self.process.pid).suspend()

            self.layout.clear_widgets()
            self.layout.add_widget(self.miniature)
            self.layout.add_widget(self.resume_button)
            self.layout.add_widget(self.stop_button)
            self.layout.add_widget(self.log_button)

    def resume_event(self, *args, **kwargs):
        if self.process is not None:
            psutil.Process(self.process.pid).resume()

            self.layout.clear_widgets()
            self.layout.add_widget(self.miniature)
            self.layout.add_widget(self.pause_button)
            self.layout.add_widget(self.stop_button)
            self.layout.add_widget(self.log_button)

    def log_event(self, *args, **kwargs):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, self.log_text)
        win32clipboard.CloseClipboard()


class ClientsWidget(ScrollView):
    def __init__(self, **kwargs):
        super(ClientsWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'

        Clock.schedule_once(self.update)
        Clock.schedule_interval(self.update, 5)

    def update(self, _):
        app_list = self.find_windows(window_name='Sky2Fly')
        s2f_actual_windows = [
            win32gui.FindWindowEx(
                win32gui.FindWindowEx(parent_hwnd, None, 'AtlAxWin100', None),
                None, 'MacromediaFlashPlayerActiveX', None
            )
            for parent_hwnd in app_list
        ]

        layout = self.ids.layout
        current_s2f_windows = {child.hwnd: child for child in layout.children}
        new_windows = {}
        if sorted(s2f_actual_windows) != sorted(list(current_s2f_windows.keys())):
            old_windows = set(current_s2f_windows.keys()).difference(s2f_actual_windows)
            for hwnd in old_windows:
                layout.remove_widget(current_s2f_windows[hwnd])
            # layout.clear_widgets()
            new_windows = set(s2f_actual_windows).difference(current_s2f_windows.keys())
            for hwnd in new_windows:
                layout.add_widget(current_s2f_windows.get(hwnd, ClientButton(hwnd=hwnd)))

        for child in layout.children:
            if child.hwnd not in new_windows:
                child.update_miniature()

    def find_windows(self, window_name=None, window_class=None):
        """Finds all windows with a title matching the given name."""
        if window_name is None and window_class is None:
            return []

        def enum_windows_callback(hwnd, window_list):
            name = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            visible = win32gui.IsWindowVisible(hwnd)
            # print(name, class_name, win32gui.GetWindowRect(hwnd), visible)
            if ((window_name is None or window_name == name)
                    and (window_class is None or window_class == class_name)
                    and visible):
                window_list.append(hwnd)
            return True

        result = []
        win32gui.EnumWindows(enum_windows_callback, result)
        return result
