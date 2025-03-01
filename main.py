import sys
import traceback
import os
from kivy.resources import resource_add_path
  
 
def custom_excepthook(exctype, value, tb):
    # Log the error to a file
    with open('error_log.txt', 'w') as f:
        f.write(''.join(traceback.format_exception(exctype, value, tb)))
    # Also print it
    print(''.join(traceback.format_exception(exctype, value, tb)))
    input("Press Enter to exit...")  # This will keep the window open

sys.excepthook = custom_excepthook
try:
    from kivy.app import App
    from screens.diary import DiaryScreen
    from screens.confirm import ConfirmationScreen
    from screens.home import HomeScreen
    from screens.history import HistoryScreen
    from kivy.uix.screenmanager import ScreenManager
    from utils.loading import load_fonts

    class Diary(App):
        def build(self):
            sm = ScreenManager()
            sm.add_widget(HomeScreen(name='home'))
            sm.add_widget(DiaryScreen(name='diary'))
            sm.add_widget(ConfirmationScreen(name='confirm'))
            sm.add_widget(HistoryScreen(name='history'))
            sm.current = 'home'
            load_fonts()
            return sm

    if __name__ == '__main__':
        if hasattr(sys, '_MEIPASS'):
            resource_add_path(sys._MEIPASS)
        Diary().run()

except Exception as e:
    with open('error_log.txt', 'w') as f:
        f.write(f"Error: {str(e)}\n")
        f.write(traceback.format_exc())
    input("Press Enter to exit...")
