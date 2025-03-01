from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from utils.loading import load_colors, resource_path

PRIMARY, SECONDARY, ACCENT, TEXT = load_colors()

class HomeConstructor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def go_to_diary(self):
        self.parent.manager.current = 'diary'

    def go_to_history(self):
        history_screen = self.parent.manager.get_screen('history')
        history_constructor = history_screen.children[0]
        history_constructor.load_entries()
        self.parent.manager.current = 'history'

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        Builder.load_file(resource_path('screens/home.kv'))
        super().__init__(**kwargs)
