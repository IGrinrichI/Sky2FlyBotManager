import os
import sys

from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeViewNode, TreeView


class PresetButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = 32
        self.color = (1, 1, 1)
        self.background_color = (.7, .7, .7)

    def on_release(self):
        selected_preset = self.parent.parent.selected_preset
        if selected_preset is not None:
            selected_preset.background_color = (.7, .7, .7)
        self.background_color = (0, 1, 0)
        self.parent.parent.selected_preset = self


class PresetsWidget(ScrollView):
    def __init__(self, **kwargs):
        super(PresetsWidget, self).__init__(**kwargs)
        self.always_overscroll = False
        self.selected_preset = None
        Clock.schedule_once(self.update)
        Clock.schedule_interval(self.update, 5)

    def update(self, _):
        layout = self.ids.layout

        if hasattr(sys, '_MEIPASS'):
            preset_dir = os.getcwd()
        else:
            preset_dir = os.path.join(os.getcwd(), 'presets')

        presets = list(filter(lambda x: x.endswith('.preset'), os.listdir(preset_dir)))
        preset_names = [preset[:-len(".preset")] for preset in presets]
        current_presets = {child.text: child for child in layout.children}

        if preset_names != list(current_presets.keys()):
            layout.clear_widgets()
            for preset_name in preset_names:
                layout.add_widget(current_presets.get(preset_name, PresetButton(text=preset_name)))

        if self.selected_preset is not None and self.selected_preset not in layout.children:
            self.selected_preset = None
