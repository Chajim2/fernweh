import requests
import sqlite3

from flask import request
from utils.loading import resource_path, UserState

URL = "https://chajim.pythonanywhere.com/"

class DiaryDatabase:
    def __init__(self):
        pass

    def add_friend(self, friend_name):
        response = requests.post(URL + "add_friend", json = {"friend_name" : friend_name, "id" : UserState.get_user_id()})
        if response.status_code > 205:
            print("UNUSUAL BEHAVIOR HERE ", response.json()['message'])
        return response.json()['message']

    def save_entry(self, text, emotions):
        response = requests.post(URL + "save_entry", json = {"emotions": emotions,"text" : text, "id" : UserState.get_user_id()})
        if response.status_code > 205:
            print("UNUSUAL BEHAVIOR HERE ", response.json()['message'])

    def get_all_entries(self):
        response = requests.post(URL + "get_all_entries", json = {"id" : UserState.get_user_id()})
        if response.status_code > 205:
            print("UNUSUAL BEHAVIOR HERE ", response.json()['message'])
        return response.json()['entries']
    
    def get_friends(self):
        response = requests.post(URL + "friends", json = {"id" : UserState.get_user_id()})
        if response.status_code > 205:
            print("UNUSUAL BEHAVIOR HERE ", response.json()['message'])
        return response.json()['friends']
