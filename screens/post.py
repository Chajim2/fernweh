from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty # Need ObjectProperty
from kivy.lang import Builder
from kivy.app import App
from utils.loading import resource_path, TEXT # Adjust path as needed
from kivy.metrics import dp
from db.db import DiaryDatabase
from kivy.uix.label import Label
from datetime import datetime # For potential formatting if needed
from kivy.clock import Clock # Import Clock
from kivy.core.window import Window

# Instantiate database connection once
db = DiaryDatabase()

Builder.load_file(resource_path('screens/post.kv')) 

class PostScreen(Screen):
    post_data = ObjectProperty({"id": None, "username": "", "text": "", "emotions": [], "timestamp": ""})
    username_text = StringProperty("")
    post_text = StringProperty("")
    emotions_text = StringProperty("")
    date_text = StringProperty("")
    id = None # Store the post ID separately for easier access

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.on_window_resize)
        Clock.schedule_once(lambda dt: self.on_window_resize(None, *Window.size))

    def on_window_resize(self, instance, width, height):
        try:
            if not self.width:  
                return
            # handling desktop, tablet and phone screen sizes
            if (width / height) > (15/9):
                padding_h = width / (4)
            elif (width / height) > 1:
                padding_h = width / 5
            else:         
                padding_h = 10
            self.ids.content_container.padding = [padding_h, 0, padding_h, 0]
        except Exception as e:
            print(f"Error in resize handler: {e}")

    def set_post_data(self, data):
        print(f"Setting post data: {data}")
        self.post_data = data
        self.id = data.get('id') # Get the post ID from the data

        if not self.id:
            print("Error: Post ID is missing in set_post_data")
            # Optionally, clear fields or show an error message
            self.username_text = "Error: Post not found"
            self.post_text = ""
            self.emotions_text = ""
            self.date_text = ""
            self._display_comments([]) # Clear comments display
            return

        # Update text properties
        self.username_text = f"Post by: {data.get('username', 'N/A')}"
        self.post_text = data.get('text', 'No content')
        emotions = data.get('emotions', [])
        self.emotions_text = f"Emotions: {', '.join(emotions) if emotions else 'None specified'}"
        self.date_text = data.get('timestamp', 'No date')

        # Load and display comments for this post
        self._load_and_display_comments()

    def _load_and_display_comments(self):
        if not self.id:
            print("Cannot load comments: Post ID is not set.")
            self._display_comments([])
            return
        try:
            comments = db.get_comments(self.id)
            print("COMNMETNS ARE: ", comments)
            self._display_comments(comments if comments else [])
        except Exception as e:
            print(f"Error fetching or displaying comments: {e}")
            self._display_comments([]) # Display empty on error

    def _display_comments(self, comments):
        """Clears and populates the comments container."""
        comments_container = self.ids.get('comments_container')
        if not comments_container:
            print("Error: comments_container not found in ids")
            # Attempt to schedule the call slightly later if ids might not be ready
            Clock.schedule_once(lambda dt: self._display_comments(comments), 0.1)
            return

        comments_container.clear_widgets()

        if not comments:
            # Optional: Add a label if there are no comments
            no_comments_label = Label(
                text="No comments yet.",
                color=(*TEXT[:3], 0.7), # Slightly dimmer text
                size_hint_y=None,
                halign='center',
                valign='middle',
                font_name = "Regular"
            )
            no_comments_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
            no_comments_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1] + dp(10))) # Add padding
            comments_container.add_widget(no_comments_label)
            return

        for comment in comments:
            # Use keys from the actual DB response format
            author_name = comment.get('author_name', 'Unknown')
            comment_text = comment.get('text', '')
          
            display_text = f"{author_name}: {comment_text}"

            comment_label = Label(
                font_name = 'Regular',
                text=display_text,
                color=TEXT,
                size_hint_y=None,
                halign='left',
                valign='top',
            )
            # Adjust text_size for wrapping and height based on texture size
            comment_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - dp(10), None))) # Adjust width for padding
            comment_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1] + dp(10))) # Add vertical padding
            comments_container.add_widget(comment_label)

    def submit_comment(self):
        """Submits a new comment and refreshes the list."""
        comment_text = self.ids.comment_input.text.strip()
        if not comment_text:
            print("Comment text is empty.")
            return
        if not self.id:
             print("Post ID missing, cannot submit comment.")
             return

        try:
            # Assuming post_comment returns (success_bool, message_str)
            success, message = db.post_comment(self.id, comment_text)
            print(f"Post comment result: {success}, {message}") # Debugging
            if success:
                # Clear input field
                self.ids.comment_input.text = ""
                # Refresh comments list immediately
                self._load_and_display_comments()
            else:
                # TODO: Show error message to user (e.g., using a popup or status label)
                print(f"Failed to post comment: {message}")
        except Exception as e:
            print(f"Error submitting comment: {e}")
            # TODO: Show error message to user

    def go_back(self):
        App.get_running_app().root.current = 'history'

    