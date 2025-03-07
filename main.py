import sys
from utils.loading import UserState
from kivy.resources import resource_add_path


from kivy.app import App
from screens.diary import DiaryScreen
from screens.confirm import ConfirmationScreen
from screens.home import HomeScreen
from screens.history import HistoryScreen
from screens.login import LoginScreen
from screens.register import RegisterScreen
from kivy.uix.screenmanager import ScreenManager
from utils.loading import load_fonts

class Diary(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(DiaryScreen(name='diary'))
        sm.add_widget(ConfirmationScreen(name='confirm'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(LoginScreen(name = 'login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.current = 'login'
        load_fonts()
        UserState.set_state("Logged out")
        return sm

if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(sys._MEIPASS)
    Diary().run()
