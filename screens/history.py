from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from utils.loading import load_colors
from db.db import DiaryDatabase
from datetime import datetime
from kivy.clock import Clock

PRIMARY, SECONDARY, ACCENT, TEXT = load_colors()

class HistoryConstructor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DiaryDatabase()
        
    def on_kv_post(self, base_widget):
        # This will be called after the kv file is loaded and ids are ready
        Clock.schedule_once(self.load_entries, 0)
    
    def load_entries(self, *args):
        entries = self.db.get_all_entries()
        entries_text = ""
        
        for entry in entries:
            # Convert timestamp string to datetime
            timestamp = datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
            formatted_date = timestamp.strftime('%B %d, %Y - %I:%M %p')
            
            # Format each entry
            entries_text += f"\n[b]{formatted_date}[/b]\n"
            entries_text += f"{entry['text']}\n"
            entries_text += f"Emotions: {', '.join(entry['emotions'])}\n"
            entries_text += "\n" + "-"*50 + "\n"  # Separator line
            
        if hasattr(self.ids, 'entries_label'):
            self.ids.entries_label.text = entries_text
    
    def go_home(self):
        self.parent.manager.current = 'home'

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        Builder.load_file('screens/history.kv')
        super().__init__(**kwargs) 