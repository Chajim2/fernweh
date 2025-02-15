from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from utils.loading import load_colors

PRIMARY, SECONDARY, ACCENT, TEXT = load_colors()

class HomeConstructor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def go_to_diary(self):
        # Navigate to diary screen
        self.parent.manager.current = 'diary'

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        Builder.load_file('screens/home.kv')
        super().__init__(**kwargs)
