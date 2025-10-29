from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

import view.clients_widget
import view.presets_widget


class MainView(BoxLayout):

    def make_hint(self, text):
        hint = Button(text=text)
        Window.add_widget(hint)
        Clock.schedule_once(lambda _: Window.remove_widget(hint), 1)


class Sky2FlyBotManagerApp(App):
    def build(self):
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
