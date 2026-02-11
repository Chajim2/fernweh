from kivy.core.text import LabelBase
import sys
import os
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import requests
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp, sp

URL = "https://chajim.pythonanywhere.com/"

def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path) 

def is_connected():
    try:
        resp = requests.get("https://google.com", timeout = 2)
        return resp.status_code == 200
    except:
         return False

def load_fonts():
    LabelBase.register(name='Italic', 
                    fn_regular=resource_path('utils/font/LiberationSerif-Italic.ttf'))
    LabelBase.register(name='BoldItalic', 
                    fn_regular=resource_path('utils/font/LiberationSerif-BoldItalic.ttf'))
    LabelBase.register(name='Bold',
                    fn_regular=resource_path('utils/font/LiberationSerif-Bold.ttf')) 
    LabelBase.register(name='Regular',
                    fn_regular=resource_path('utils/font/LiberationSerif-Regular.ttf'))

def show_popup(message):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        label = Label(
            text=message,
            font_name="Regular",
            font_size=sp(18),
            color=TEXT
        )
        content.add_widget(label)
        
        popup = Popup(
            title='Login Status',
            content=content,
            size_hint=(0.6, 0.4),
            title_font="Regular",
            title_size=sp(20),
            title_color=TEXT,
            background_color=SECONDARY,
            separator_color=ACCENT
        )
        popup.open()

def load_colors():
    PRIMARY = (15.7/100, 17.3/100, 20.4/100, 1)
    SECONDARY = (62/255, 68/255, 81/ 255, 1)
    ACCENT = (97/255,175/255,239/255, 1)
    TEXT = (180/255, 184/255, 193/255, 1)

    return PRIMARY, SECONDARY, ACCENT, TEXT

PRIMARY, SECONDARY, ACCENT, TEXT = load_colors()

def fake_get_emotions(text):
    return [["sad" , "u real sad bro"], ['hopeful', 'u might not be completely cooked g'], ['lost' , 'lost in the heat of it all']]

class UserState:
    state = "Logged Out"
    user_id = None
    @classmethod
    def set_state(cls, state):
         cls.state = state
    @classmethod
    def get_state(cls):
         return cls.state
    @classmethod
    def set_user_id(cls, user_id):
        cls.user_id = user_id 

    @classmethod
    def get_user_id(cls):
        return cls.user_id 
    
    