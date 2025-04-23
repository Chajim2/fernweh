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
            font_name="Bold"
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

class HistoryConstructor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DiaryDatabase()
        #Clock.schedule_once(self.load_entries)

    def load_entries(self, *args):
        if not self.ids or 'entries_container' not in self.ids:
             Clock.schedule_once(self.load_entries, 0.1) # Try again shortly
             return

        friends = self.db.get_friends()
        entries_container = self.ids.entries_container
        entries_container.clear_widgets()
        print("Attempting to load entries...") # Debugging

        all_entries_data = [] # List to hold all entries with parsed timestamps

        if friends is None:
            friends = [] # Ensure friends is a list even if API returns None

        friends.append({"id" : UserState.get_user_id(), "username" : "you"})

        for friend in friends:
            friend_username = friend.get('username', 'Unknown User')
            try:
                entries = self.db.get_all_entries(id = friend['id'])
                if entries is None:
                    print(f"No entries found or error fetching for {friend_username}")
                    continue # Skip this friend if entries are None

                for entry in entries:
                    try:
                        timestamp_str = entry.get('timestamp', '')
                        parsed_timestamp = None
                        formatted_date = "Unknown Date"

                        if isinstance(timestamp_str, str) and timestamp_str:
                            try:
                                parsed_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                                formatted_date = parsed_timestamp.strftime('%B %d, %Y - %I:%M %p')
                            except ValueError:
                                print(f"Warning: Could not parse timestamp '{timestamp_str}' for entry {entry.get('id')}")
                                # Assign a default old date for sorting if parsing fails
                                parsed_timestamp = datetime.min
                        else:
                             # Assign a default old date if timestamp is missing or not a string
                             parsed_timestamp = datetime.min

                        # Ensure emotions is a list/tuple
                        emotions_list = entry.get('emotions', [])
                        if not isinstance(emotions_list, (list, tuple)):
                            emotions_list = []

                        all_entries_data.append({
                            'username': friend_username,
                            'timestamp_obj': parsed_timestamp,
                            'formatted_date': formatted_date,
                            'text': entry.get('text', 'N/A'),
                            'emotions': emotions_list,
                            'id': entry.get("id")
                        })
                    except Exception as e:
                        print(f"Error processing individual entry for {friend_username}: {e}")
                        print(f"Problematic entry data: {entry}")
            except Exception as e:
                 print(f"Error fetching entries for friend {friend_username} (ID: {friend.get('id')}): {e}")

        # Sort all collected entries by timestamp object, newest first
        all_entries_data.sort(key=lambda x: x['timestamp_obj'], reverse=True)

        entry_count = 0
        for entry_data in all_entries_data:
            try:
                post = PostPanel(
                    username=entry_data['username'],
                    timestamp=entry_data['formatted_date'],
                    text=entry_data['text'],
                    emotions=entry_data['emotions'],
                    id=entry_data['id']
                )
                entries_container.add_widget(post)
                entry_count += 1
            except Exception as e:
                print(f"Error creating PostPanel for entry ID {entry_data.get('id')}: {e}")

        if entry_count == 0:
            print("No entries were added to the container.")
            # Optional: Add a label indicating no entries
            entries_container.add_widget(Label(
                text="No entries found for you or your friends.",
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
