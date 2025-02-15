from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from utils.loading import load_colors
from db.db import DiaryDatabase

PRIMARY, SECONDARY, ACCENT, TEXT = load_colors()

class ConfirmationScreen(Screen):
    def __init__(self, **kwargs):
        Builder.load_file('screens/confirm.kv')
        super().__init__(**kwargs)
        self.diary_text = ""
        self.emotions = []
        self.db = DiaryDatabase()
        


    def display_summary(self, diary_text, emotions):
        self.diary_text = diary_text
        self.emotions = emotions
        # Update the labels with the diary text and emotions
        self.ids.diary_preview.text = diary_text
        self.ids.emotions_summary.text = "Selected emotions:\n" + "\n".join(emotions)
    
    def confirm_entry(self):
        # Save to database
        self.db.save_entry(self.diary_text, self.emotions)
        
        # Get the main screen and clear its input
        main_screen = self.manager.get_screen('diary')
        diary_constructor = main_screen.children[0]  # Get the DiaryConstructor instance
        diary_constructor.ids.diary_input.text = ""  # Clear the text input
        diary_constructor.chosen = []  # Clear the emotions list
        
        # Clear the confirmation screen's stored data
        self.diary_text = ""
        self.emotions = []
        
        # Return to home screen instead of diary screen
        self.manager.current = 'home'
    
    def go_back(self):
        self.manager.current = 'diary'