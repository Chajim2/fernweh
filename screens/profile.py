from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.label import Label
from utils.loading import resource_path, UserState, show_popup
from db.db import DiaryDatabase
from kivy.uix.button import Button
from kivy.properties import StringProperty

class FriendLabel(Label):
    def __init__(self, friend_name, **kwargs):
        super().__init__(**kwargs)
        self.text = friend_name
        

class RequestLabel(BoxLayout):
    def __init__(self, friend_name, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.label = Label(text= friend_name)
        self.add_widget(self.label)
        
        self.accept_btn = Button(
            text='Accept',
            size_hint_x=0.3
        )
        self.add_widget(self.accept_btn)
        
        self.decline_btn = Button(
            text='Decline',
            size_hint_x=0.3
        )
        self.add_widget(self.decline_btn)

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        Builder.load_file(resource_path('screens/profile.kv'))
        super().__init__(**kwargs)
        self.db = DiaryDatabase()
        self.friends = []
        self.requests = []  # Initialize requests list
    
    def send_friend_request(self, username):
        if username.strip():
            success, message = self.db.send_friend_request(username)
            if success:
                self.ids.friend_input.text = ""  
                self.update_friends_list()
            show_popup(message)
    
    def on_enter(self, *args):
        self.update_friends_list()
        self.update_requests_list()
        
    def update_friends_list(self):
        self.ids.friends_container.clear_widgets()
        self.friends = self.db.get_friends()
        if self.friends:
            for friend in self.friends:
                print("FRIEND IS ", friend)
                self.ids.friends_container.add_widget(
                    FriendLabel(friend_name=friend['username'])
                )
    
    def update_requests_list(self):
        self.ids.requests_container.clear_widgets()
        self.requests = self.db.get_requests()
        if self.requests:
            for request in self.requests:
                request_label = RequestLabel(friend_name=request)
                request_label.accept_btn.bind(
                    on_press=lambda x, username=request: self.accept_request(username)
                )
                request_label.decline_btn.bind(
                    on_press=lambda x, username=request: self.decline_request(username)
                )
                self.ids.requests_container.add_widget(request_label)

    
    def accept_request(self, username):
        success, message = self.db.accept_friend_request(username)
        if success:
            show_popup("Friend request accepted!")
            self.update_requests_list()
            self.update_friends_list()
        else:
            show_popup(message)

    def decline_request(self, username):
        success, message = self.db.decline_friend_request(username)
        if success:
            show_popup("Friend request declined")
            self.update_requests_list()
        else:
            show_popup(message)

    def go_to_home(self):
        self.manager.current = 'home'
        