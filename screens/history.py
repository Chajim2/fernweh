from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from utils.loading import UserState, load_colors
from db.db import DiaryDatabase
from datetime import datetime
from kivy.clock import Clock
from utils.loading import resource_path
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior 
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ColorProperty 
from kivy.app import App
from utils.loading import UserState

PRIMARY, SECONDARY, ACCENT, TEXT = load_colors()

class PostPanel(ButtonBehavior, BoxLayout):
    panel_color = ColorProperty([1, 1, 1, 0.1]) # Slightly transparent white, adjust as needed
    def __init__(self, username, timestamp, text, emotions, id, **kwargs):
        super().__init__(**kwargs)
        if UserState.get_state() == "Logged Out":
            return 
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(5)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height')) # Make height adaptive
        self.size_hint_x = 0.9
        self.pos_hint = {'x': 0} # Align to the left

        self.username = username 
        self.timestamp = timestamp
        self.text = text
        self.emotions = emotions
        self.id = id
        self.font_name = "Regular"

        # --- Background ---
        self.canvas.before.add(Color(rgba=self.panel_color))
        self.bg_rect = RoundedRectangle(radius=[dp(5)])
        self.canvas.before.add(self.bg_rect)
        self.bind(pos=self._update_bg_rect, size=self._update_bg_rect)

        # Emotions at the top
        emotions_label = Label(
            text=f"Emotions: {', '.join(emotions)}",
            color=TEXT,
            size_hint_y=None,
            halign='left',
            valign='top',
            font_name="Regular"
        )
        emotions_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.add_widget(emotions_label)

        username_label = Label(
            text=f'{username} - {timestamp}',
            color=TEXT,
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        username_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.add_widget(username_label)

        # Show only first 70 words
        words = text.split()
        preview_text = ' '.join(words[:70])
        if len(words) > 70:
            preview_text += '...'

        text_label = Label(
            text=preview_text,
            color=TEXT,
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        text_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.add_widget(text_label)

        # Initial text_size update needs a small delay
        Clock.schedule_once(self._update_label_text_size, 0.05)

    def _update_bg_rect(self, *args):
        """Callback to update background rectangle size and position."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_label_text_size(self, *args):
        """Update text_size of labels based on current width."""
        width_for_text = self.width - self.padding[0] - self.padding[2]
        if width_for_text <= 0: 
            return
            
        for child in self.children:
            if isinstance(child, Label):
                # Set text_size to enable wrapping and height calculation
                child.text_size = (width_for_text, None)

    def on_size(self, instance, value):
         Clock.schedule_once(self._update_label_text_size, 0)

    def on_press(self):
        print("GOT NAINOIFSNOIN")
        App.get_running_app().root.get_screen("post").set_post_data({"id": self.id, "username" : self.username, "emotions" : self.emotions, "text" : self.text, "timestamp" : self.timestamp})
        App.get_running_app().root.current = 'post'

class CommentPanel(ButtonBehavior, BoxLayout):
    panel_color = ColorProperty([1, 1, 1, 0.05])  # Even more transparent than posts
    def __init__(self, username, timestamp, text, post_id, **kwargs):
        super().__init__(**kwargs)
        if UserState.get_state() == "Logged Out":
            return 
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(5)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self.size_hint_x = 0.85  # Slightly smaller than posts
        self.pos_hint = {'x': 0.05}  # Indented from the left

        self.username = username 
        self.timestamp = timestamp
        self.text = text
        self.post_id = post_id
        self.font_name = "Regular"

        # --- Background ---
        self.canvas.before.add(Color(rgba=self.panel_color))
        self.bg_rect = RoundedRectangle(radius=[dp(5)])
        self.canvas.before.add(self.bg_rect)
        self.bind(pos=self._update_bg_rect, size=self._update_bg_rect)

        username_label = Label(
            text=f'{username} commented - {timestamp}',
            color=TEXT,
            size_hint_y=None,
            halign='left',
            valign='top',
            font_name="Regular"
        )
        username_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.add_widget(username_label)

        text_label = Label(
            text=text,
            color=TEXT,
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        text_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.add_widget(text_label)

        Clock.schedule_once(self._update_label_text_size, 0.05)

    def _update_bg_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_label_text_size(self, *args):
        width_for_text = self.width - self.padding[0] - self.padding[2]
        if width_for_text <= 0: 
            return
            
        for child in self.children:
            if isinstance(child, Label):
                child.text_size = (width_for_text, None)

    def on_size(self, instance, value):
         Clock.schedule_once(self._update_label_text_size, 0)

    def on_press(self):
        App.get_running_app().root.get_screen("post").set_post_data({"id": self.post_id})
        App.get_running_app().root.current = 'post'

class HistoryConstructor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DiaryDatabase()

    def load_entries(self, *args):
        if not self.ids or 'entries_container' not in self.ids:
             Clock.schedule_once(self.load_entries, 0.1)
             return

        entries_container = self.ids.entries_container
        entries_container.clear_widgets()
        print("Loading timeline...")

        # Show loading indicator
        app = App.get_running_app()
        app.show_loading()

        try:
            # Get all entries and comments in chronological order
            timeline_items = self.db.get_all_entries(UserState.get_user_id())
            
            if timeline_items is None:
                entries_container.add_widget(Label(
                    text="Error loading timeline. Please try again.",
                    color=TEXT,
                    size_hint_y=None,
                    height=dp(50)
                ))
                return

            entry_count = 0
            for item in timeline_items:
                try:
                    if item['type'] == 'post':
                        panel = PostPanel(
                            username=item['username'],
                            timestamp=item['timestamp'],
                            text=item['text'],
                            emotions=item['emotions'],
                            id=item['id']
                        )
                    else:  # comment
                        panel = CommentPanel(
                            username=item['username'],
                            timestamp=item['timestamp'],
                            text=item['text'],
                            post_id=item['id']  # id is post_id for comments
                        )
                    entries_container.add_widget(panel)
                    entry_count += 1
                except Exception as e:
                    print(f"Error creating panel for item: {e}")

            if entry_count == 0:
                entries_container.add_widget(Label(
                    text="No entries or comments found.",
                    color=TEXT,
                    size_hint_y=None,
                    height=dp(50)
                ))
        except Exception as e:
            print(f"Error loading timeline: {e}")
            entries_container.add_widget(Label(
                text="An error occurred while loading the timeline.",
                color=TEXT,
                size_hint_y=None,
                height=dp(50)
            ))
        finally:
            # Hide loading indicator
            app.hide_loading()

    def go_home(self):
        self.parent.manager.current = 'home'
        
class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        Builder.load_file(resource_path('screens/history.kv'))
        super().__init__(**kwargs)
