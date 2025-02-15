from kivy.app import App
from screens.diary import DiaryScreen
from screens.confirm import ConfirmationScreen
from screens.home import HomeScreen
from screens.history import HistoryScreen
from kivy.uix.screenmanager import ScreenManager

class Diary(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(DiaryScreen(name='diary'))
        sm.add_widget(ConfirmationScreen(name='confirm'))
        sm.add_widget(HistoryScreen(name='history'))
        # Set initial screen to home
        sm.current = 'home'
        return sm

if __name__ == '__main__':
    Diary().run()
