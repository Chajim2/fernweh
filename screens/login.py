from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
import requests
from utils.loading import resource_path, UserState, show_popup, is_connected

URL = "https://chajim.pythonanywhere.com/login"


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        Builder.load_file(resource_path('screens/login.kv'))  # Load the KV file
        super().__init__(**kwargs)

    def login(self):
        username = self.ids.username.text
        password = self.ids.password.text
        self.ids.password.text = ""
        if username and password: 
            #sending data to db server
            hashed = bcrypt.hashpw(password, bcrypt.gensalt())
            response = requests.post(URL, json={"username": username, 'password': hashed})
            if response is None:
                show_popup("No response from the server")
                return
            json_data = response.json()
            if response.status_code == 200:  # Check for successful login message
                UserState.set_state("Logged In")
                UserState.set_user_id(json_data['id'])
                show_popup("Successful Login")  
                self.parent.current = "home"
            else:
                show_popup(json_data['message']) 
        else:
            show_popup("Please enter both username and password.")
    
    def to_register(self):
        self.parent.current = "register"

    
   