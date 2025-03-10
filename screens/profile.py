from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.label import Label
from utils.loading import resource_path, UserState
from db.db import DiaryDatabase

class FriendLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        Builder.load_file(resource_path('screens/profile.kv'))
        super().__init__(**kwargs)
        self.db = DiaryDatabase()
        
    def add_friend(self, username):
        # Add friend logic here
        if username.strip():
            success = self.db.add_friend(UserState.get_user_id(), username)
            if success:
                self.ids.friend_input.text = ""  # Clear input
                self.update_friends_list()
    
    def update_friends_list(self):
        # Clear current list
        self.ids.friends_container.clear_widgets()
        # Get and display friends
        friends = self.db.get_friends(UserState.get_user_id())
        for friend in friends:
            self.ids.friends_container.add_widget(
                FriendLabel(text=friend['username'])
            ) 