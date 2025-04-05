from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from utils.loading import load_colors
from db.db import DiaryDatabase
from datetime import datetime
from kivy.clock import Clock
from utils.loading import resource_path

PRIMARY, SECONDARY, ACCENT, TEXT = load_colors()

class HistoryConstructor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DiaryDatabase()
        
    #def on_kv_post(self, base_widget):
     #   Clock.schedule_once(self.load_entries, 0)
    
    def on_enter(self, *args):
        self.load_entries()

    def load_entries(self, *args):
        friends = self.db.get_friends()
        entries_text = ""
        for friend in friends:
            entries = self.db.get_all_entries(id = friend['id'])
            print("FRIEND", friend, entries)
            for entry in entries:
                timestamp = datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
                formatted_date = timestamp.strftime('%B %d, %Y - %I:%M %p')
                entries_text += f"\n[b]{friend['username']}[/b]"
                entries_text += f"\n{formatted_date}\n"
                entries_text += f"{entry['text']}\n"
                entries_text += f"Emotions: {', '.join(entry['emotions'])}\n"
                entries_text += "\n" + "-"*50 + "\n"  # Separator line
                
            if hasattr(self.ids, 'entries_label'):
                self.ids.entries_label.text = entries_text
    
    def go_home(self):
        self.parent.manager.current = 'home'

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        Builder.load_file(resource_path('screens/history.kv'))
        super().__init__(**kwargs) 