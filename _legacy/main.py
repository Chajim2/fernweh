import sys
from utils.loading import UserState
from kivy.resources import resource_add_path
from utils.widgets import StyledButton, StyledTextInput, StyledLabel, RoundedLabel

from kivy.app import App
from screens.diary import DiaryScreen
from screens.confirm import ConfirmationScreen
from screens.home import HomeScreen
from screens.history import HistoryScreen
from screens.profile import ProfileScreen
from screens.login import LoginScreen
from screens.register import RegisterScreen
from screens.post import PostScreen
from kivy.uix.screenmanager import ScreenManager
from utils.loading import load_fonts
from kivy.uix.popup import Popup
from kivy.uix.label import Label

class Diary(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(DiaryScreen(name='diary'))
        sm.add_widget(ConfirmationScreen(name='confirm'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(LoginScreen(name = 'login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(PostScreen(name = 'post'))
        sm.current = 'login'
        load_fonts()
        UserState.set_state("Logged out")
        return sm

    def show_loading(self):
        self.loading_popup = Popup(
            title='Loading',
            content=Label(text='Please wait...'),
            size_hint=(0.6, 0.4)
        )
        self.loading_popup.open()

    def hide_loading(self):
        if hasattr(self, 'loading_popup'):
            self.loading_popup.dismiss()

class UserState:
    _state = "Logged Out"
    _user_id = None
    _token = None
    
    @classmethod
    def set_state(cls, state):
        cls._state = state
        if state == "Logged Out":
            cls._user_id = None
            cls._token = None

if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(sys._MEIPASS)
    Diary().run()
