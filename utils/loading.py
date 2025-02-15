from kivy.core.text import LabelBase
from utils.ai import get_emotions
import time

def load_fonts():
    LabelBase.register(name='Italic', 
                    fn_regular='utils/font/LiberationSerif-Italic.ttf')
    LabelBase.register(name='BoldItalic', 
                    fn_regular='utils/font/LiberationSerif-BoldItalic.ttf')
    LabelBase.register(name='Bold',
                    fn_regular='utils/font/LiberationSerif-Bold.ttf') 
    LabelBase.register(name='Regular',
                    fn_regular='utils/font/LiberationSerif-Regular.ttf')

def load_colors():
    PRIMARY = (15.7/100, 17.3/100, 20.4/100, 1)
    SECONDARY = (62/255, 68/255, 81/ 255, 1)
    ACCENT = (97/255,175/255,239/255, 1)
    TEXT = (180/255, 184/255, 193/255, 1)

    return PRIMARY, SECONDARY, ACCENT, TEXT

PRIMARY, SECONDARY, ACCENT, TEXT = load_colors()

def fake_get_emotions(text):
    return [["sad" , "u real sad bro"], ['hopeful', 'u might not be completely cooked g'], ['lost' , 'lost in the heat of it all']]

def save_entry(name, text):
    pass