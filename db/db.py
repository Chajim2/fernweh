import requests
import sqlite3

from flask import request
from utils.loading import resource_path, UserState

URL = "https://chajim.pythonanywhere.com/"

class DiaryDatabase:
    def __init__(self):
        pass
    
    def get_emotions(self, text):
        response = requests.post(URL + "get_emotions", json={"text" : text})
        if response.status_code > 205:
            print("UNUSUAL BEHAVIOR HERE ", response.json()['message'])
        emotions = []
        for line in response.json()['emotions']:
            emotions.extend([[line['emotion'], line['description']]])
        return emotions

    def send_friend_request(self, friend_name):
        response = requests.post(URL + "send_friend_request", json={"id" : UserState.get_user_id(), 'friend_name' : friend_name})
        if response.status_code > 205:
            print("UNUSUAL BEHAVIOR HERE ", response.json()['message'])
        return response.status_code == 200, response.json()['message']
    
    def get_requests(self):
        response = requests.post(URL + "get_requests", json={"id" : UserState.get_user_id()})
        print("STATUS KOD " ,response.status_code)
        if response.status_code > 205:
            print("UNUSUAL BEHAVIOR HERE ", response.json()['message'])
        return response.json()['requests']
    
    def add_friend(self, friend_name):
        response = requests.post(URL + "add_friend", json = {"friend_name" : friend_name, "id" : UserState.get_user_id()})
        if response.status_code > 205:
            print("UNUSUAL BEHAVIOR HERE ", response.json()['message'])
        return response.status_code == 201, response.json()['message']

    def save_entry(self, text, emotions):
        response = requests.post(URL + "save_entry", json = {"emotions": emotions,"text" : text, "id" : UserState.get_user_id()})
        if response.status_code > 205:
            print("UNUSUAL BEHAVIOR HERE ", response.json()['message'])

    def get_all_entries(self, id = UserState.get_user_id()):
        response = requests.post(URL + "get_all_entries", json = {"id" : id})
        if response.status_code > 205:
            print("UNUSUAL BEHAVIOR HERE ", response.json()['message'])
        return response.json()['entries']
    
    def accept_friend_request(self, friend_name):
        response = requests.post(URL + "accept_friend_request", json ={"id" : UserState.get_user_id(), "friend_name" : friend_name})
        if response.status_code > 205:
            print("UNUSUAL BEHAVIOR HERE ", response.json()['message'])
        return response.status_code == 200, response.json()['message']
    
    def decline_friend_request(self, friend_name):
        response = requests.post(URL + "decline_friend_request", json ={"id" : UserState.get_user_id(), "friend_name" : friend_name})
        if response.status_code > 205:
            print("UNUSUAL BEHAVIOR HERE ", response.json()['message'])
        return response.status_code == 200, response.json()['message']

    def get_friends(self):
        response = requests.post(URL + "get_friends", json = {"id" : UserState.get_user_id()})
        if response.status_code > 205:
            if response:
                print("UNUSUAL BEHAVIOR HERE ", response.json()['message'])
            else:
                print("NO RESPONSE RECEIVED")
            return
        return response.json()['friends']
