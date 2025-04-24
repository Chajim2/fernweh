import json
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
import requests
from utils.loading import resource_path, UserState, show_popup
import bcrypt

URL = "https://chajim.pythonanywhere.com/register"

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        Builder.load_file(resource_path('screens/register.kv'))  # Load the KV file
        super().__init__(**kwargs)

    def register(self):
        print("GOT HERE")
        username = self.ids.username.text
        password = self.ids.password.text
        if username and password:
            if len(password) < 5:
                show_popup("Password is too short")
                return
            
            hashed = bcrypt.hashpw(password, bcrypt.gensalt())
            #sending data to db server
            response = requests.post(URL, json={"username": username, 'password': hashed})
            if response is None:
                show_popup("No response from the server")
                return
            json_data = response.json()
            print(json_data)
            if json_data['message'] == "User added successfully":
                show_popup("Successful register, please login")  
                self.parent.current = "login"

            elif json_data['message'] == "Username taken":
                show_popup("Username taken")
            elif json_data['message'] == "Password too short":
                show_popup("Password too short")
            else:
                show_popup("Error with adding user")
        else:
            show_popup("Please enter both username and password.")
    
    def to_login(self):
        self.parent.current = "login"
         
    
   