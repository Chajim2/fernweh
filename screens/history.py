from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from utils.loading import UserState, load_colors
from db.db import DiaryDatabase
from datetime import datetime
from kivy.clock import Clock
from utils.loading import resource_path
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.metrics import dp
# Remove Window import if only used for text_size before
# from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, InstructionGroup # Added InstructionGroup
from kivy.properties import ColorProperty # Added ColorProperty

PRIMARY, SECONDARY, ACCENT, TEXT = load_colors()

class PostPanel(BoxLayout):
    panel_color = ColorProperty([1, 1, 1, 0.1]) # Slightly transparent white, adjust as needed

    def __init__(self, username, timestamp, text, emotions, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(5)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height')) # Make height adaptive
        self.size_hint_x = 0.9
        self.pos_hint = {'x': 0} # Align to the left

        # --- Background ---
        self.canvas.before.add(Color(rgba=self.panel_color))
        self.bg_rect = RoundedRectangle(radius=[dp(5)])
        self.canvas.before.add(self.bg_rect)
        self.bind(pos=self._update_bg_rect, size=self._update_bg_rect)
        # --- End background ---

        # --- Labels (Corrected Binding) ---

        # Label 1: Username & Timestamp
        username_label = Label(
            text=f'{username} - {timestamp}',
            color=TEXT,
            size_hint_y=None,
            # text_size is set below and updated in _update_label_text_size
            halign='left',
            valign='top'
        )
        # Bind AFTER creation
        username_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.add_widget(username_label)

        # Label 2: Text Content
        text_label = Label(
            text=text,
            color=TEXT,
            size_hint_y=None,
            # text_size is set below and updated in _update_label_text_size
            halign='left',
            valign='top'
        )
        # Bind AFTER creation
        text_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.add_widget(text_label)

        # Label 3: Emotions
        emotions_label = Label(
            text=f"Emotions: {', '.join(emotions)}",
            color=TEXT,
            size_hint_y=None,
            # text_size is set below and updated in _update_label_text_size
            halign='left',
            valign='top'
        )
        # Bind AFTER creation
        emotions_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.add_widget(emotions_label)

        # Initial text_size update needs a small delay
        Clock.schedule_once(self._update_label_text_size, 0.05)

    def _update_bg_rect(self, *args):
        """Callback to update background rectangle size and position."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_label_text_size(self, *args):
        """Update text_size of labels based on current width."""
        # Recalculate width available for text inside padding
        width_for_text = self.width - self.padding[0] - self.padding[2] # Subtract left/right padding
        if width_for_text <= 0: # Avoid negative/zero width if layout not ready
            return
            
        # Iterate over children (which are the labels)
        for child in self.children:
            if isinstance(child, Label):
                # Set text_size to enable wrapping and height calculation
                child.text_size = (width_for_text, None)
                # The texture_size binding will automatically update the height

    def on_size(self, instance, value):
         Clock.schedule_once(self._update_label_text_size, 0)


class HistoryConstructor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DiaryDatabase()
        # Load entries when the widget is ready, not just on screen enter
        Clock.schedule_once(self.load_entries) # Load once layout is settled

    def load_entries(self, *args):
        # Ensure ids are available
        if not self.ids or 'entries_container' not in self.ids:
             Clock.schedule_once(self.load_entries, 0.1) # Try again shortly
             return

        friends = self.db.get_friends()
        entries_container = self.ids.entries_container
        entries_container.clear_widgets()
        print("Attempting to load entries...") # Debugging

        entry_count = 0
        friends.append({"id" : UserState.get_user_id(), "username" : "you"})
        for friend in friends:
            entries = self.db.get_all_entries(id = friend['id'])
            for entry in entries:
                try:
                    # Defensive parsing
                    timestamp_str = entry.get('timestamp', '')
                    text_content = entry.get('text', 'N/A')
                    emotions_list = entry.get('emotions', [])
                    
                    # Ensure timestamp is a string before parsing
                    if isinstance(timestamp_str, str) and timestamp_str:
                         timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                         formatted_date = timestamp.strftime('%B %d, %Y - %I:%M %p')
                    else:
                         formatted_date = "Unknown Date"

                    # Ensure emotions is a list/tuple
                    if not isinstance(emotions_list, (list, tuple)):
                        emotions_list = []


                    post = PostPanel(
                        username=friend.get('username', 'Unknown User'),
                        timestamp=formatted_date,
                        text=text_content,
                        emotions=emotions_list
                        # panel_color=[0.9, 0.9, 0.9, 0.8] # Optional: Assign a color per post
                    )
                    entries_container.add_widget(post)
                    entry_count += 1 # Increment debug counter
                except Exception as e:
                    print(f"Error processing entry for {friend.get('username', 'Unknown')}: {e}")
                    print(f"Problematic entry data: {entry}")

        if entry_count == 0:
            print("No entries were added to the container.")
            # Optional: Add a label indicating no entries
            entries_container.add_widget(Label(
                text="No entries found for your friends.",
                color=TEXT,
                size_hint_y=None,
                height=dp(50)
            ))


    def go_home(self):
        self.parent.manager.current = 'home'
        


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        Builder.load_file(resource_path('screens/history.kv'))
        super().__init__(**kwargs)
