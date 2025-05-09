from traceback import print_tb
import requests
import sqlite3
from typing import List, Tuple, Optional, Dict, Any

from flask import request
from utils.loading import resource_path, UserState

URL = "https://chajim.pythonanywhere.com/"

class DiaryDatabase:
    def __init__(self):
        pass
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Tuple[bool, Any, Optional[str]]:
        """Helper method to standardize API requests and error handling"""
        try:
            response = requests.post(URL + endpoint, json=data)
            
            if response is None:
                return False, None, "No response received from server"
                
            if response.status_code != 200:
                return False, None, f"Server returned status code: {response.status_code}"
                
            try:
                return True, response.json(), None
            except requests.exceptions.JSONDecodeError as e:
                return False, None, f"Failed to parse server response: {e}"
                
        except requests.exceptions.RequestException as e:
            return False, None, f"Network error occurred: {e}"
    
    def get_emotions(self, text: str) -> List[List[str]]:
        success, data, error = self._make_request("get_emotions", {"text": text, "id": UserState.get_user_id()})
        if not success:
            print(f"Error getting emotions: {error}")
            return []
            
        emotions = []
        for line in data['emotions']:
            emotions.append([line['emotion'], line['description']])
        return emotions

    def post_comment(self, post_id: str, text: str) -> Tuple[bool, str]:
        success, data, error = self._make_request("post_comment", {
            "text": text, 
            "post_id": post_id, 
            "id": UserState.get_user_id()
        })
        if not success:
            return False, f"Error posting comment: {error}"
        return True, data['message']
    
    def get_comments(self, post_id: str) -> List[Dict[str, Any]]:
        success, data, error = self._make_request("get_comments", {
            "entry_id": post_id, 
            "id": UserState.get_user_id()
        })
        if not success:
            print(f"Error getting comments: {error}")
            return []
        return data['comments']
    
    def send_friend_request(self, friend_name: str) -> Tuple[bool, str]:
        success, data, error = self._make_request("send_friend_request", {
            "id": UserState.get_user_id(), 
            'friend_name': friend_name
        })
        if not success:
            return False, f"Error sending friend request: {error}"
        return True, data['message']
    
    def get_requests(self) -> List[Dict[str, Any]]:
        success, data, error = self._make_request("get_requests", {"id": UserState.get_user_id()})
        if not success:
            print(f"Error getting requests: {error}")
            return []
        return data['requests']
    
    def save_entry(self, text: str, emotions: List[List[str]]) -> Tuple[bool, str]:
        success, data, error = self._make_request("save_entry", {
            "emotions": emotions,
            "text": text, 
            "id": UserState.get_user_id()
        })
        if not success:
            return False, f"Error saving entry: {error}"
        return True, data['message']

    def get_all_entries(self, id: str = UserState.get_user_id()) -> List[Dict[str, Any]]:
        success, data, error = self._make_request("get_all_entries", {"id": id})
        if not success:
            print(f"Error getting entries: {error}")
            return []
        return data['entries']
    
    def accept_friend_request(self, friend_name: str) -> Tuple[bool, str]:
        success, data, error = self._make_request("accept_friend_request", {
            "id": UserState.get_user_id(), 
            "friend_name": friend_name
        })
        if not success:
            return False, f"Error accepting friend request: {error}"
        return True, data['message']
    
    def decline_friend_request(self, friend_name: str) -> Tuple[bool, str]:
        success, data, error = self._make_request("decline_friend_request", {
            "id": UserState.get_user_id(), 
            "friend_name": friend_name
        })
        if not success:
            return False, f"Error declining friend request: {error}"
        return True, data['message']

    def get_friends(self) -> List[Dict[str, Any]]:
        success, data, error = self._make_request("get_friends", {"id": UserState.get_user_id()})
        if not success:
            print(f"Error getting friends: {error}")
            return []
        return data['friends']
