from flask import Flask, request, jsonify
from scripts.db import DiaryDatabase
from scripts.ai import LLMCaller
import logging
import jwt
from jwt import InvalidTokenError
from functools import wraps
from dotenv import load_dotenv
import os
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
from scripts.auth import require_jwt, create_refresh_jwt, create_auth_jwt, SECRET_KEY, ALGORITHM
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
with app.app_context():
    db = DiaryDatabase()

CORS(app)
 
llmcaller = LLMCaller()

 

@app.route('/')
def hello_world():
    return "Nun to see here friend"

@app.route('/refresh', methods = ["POST"])
def refresh():
    data = request.get_json()
    if not data or 'refresh_token' not in data:
            return jsonify({'error': 'Refresh is missing in request body'}), 401

    token = data['refresh_token']
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return jsonify({"auth_token": create_auth_jwt({"id" : payload['id']})})
 
    except InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

@app.route('/get_emotions', methods = ["POST"])
@require_jwt
def get_emotions(id, data):
    if request.method == "POST":
        if data is None:
            return jsonify({"message": "Invalid JSON"}), 400

        emotions = llmcaller.call_llm(data['text'])
        formated_emotions = []
        for line in emotions.split(";"):
            if ":" in line:
                emotion, description = line.split(":", 1)
                formated_emotions.append({"emotion" : emotion.strip(), "description" : description.strip()})
        return jsonify({"emotions": formated_emotions, "message" : "Worked"}), 200


@app.route('/login', methods = ['POST'])
def login():
    username, password = request.get_json()['username'], request.get_json()['password']
    users_found = list(db.check_login(username, password))
    if len(users_found) == 0:
        return jsonify({"message": "User not found"}), 404
    else:
        auth_token = create_auth_jwt({'id': users_found[0][0]})
        refresh_token = create_refresh_jwt({"id" : users_found[0][0]})
        return jsonify({"message" : "Successfull login", "id" : auth_token, 'refresh_token' : refresh_token}), 200

@app.route('/register', methods = ['POST'])
def register():
    username, password = request.get_json()['username'], request.get_json()['password']
    if db.username_taken(username):
        return jsonify({"message": "Username taken"}), 409
    else:
        db.add_user(username, password)
        return jsonify({"message": "User added successfully"}), 201

@app.route('/add_friend', methods = ['POST'])
@require_jwt
def add_friend(id, data):
    result = db.add_friend(data['friend_name'], id)

    if result == 0:
        return jsonify({"message" : "Friend not found"}), 404

    if result == 1:
        return jsonify({"message" : "Already friends"}), 409

    return jsonify({'message' : "Friend added successfully"}), 201

@app.route('/save_entry', methods = ['POST'])
@require_jwt
def save_entry(id, data):
    if db.save_entry(data['text'], data['emotions'], id):
        chunks = llmcaller.get_pieces_to_vector(data['text'])
        chunks = json.loads(chunks)
        print(chunks, type(chunks))
        #TODO implement the vectorization
        
        #profile = db.get_user_profile(id)
        #if profile and 'summary' in profile:
         #   llmcaller.update_user_summary(data['text'], profile['summary'])
        
        return jsonify({"message": "Entry saved", "chunks" : chunks}), 201
    else:
        return jsonify({"message": "Error while trying to save entry"}), 400

@app.route ('/get_all_entries', methods = ["POST"])
@require_jwt
def get_all_entries(id, data):
    results = db.get_all_entries(id)
    for friend in db.get_friends(id):
        results.extend(db.get_all_entries(friend['id']))
    #might have to tweak this later
    sorted_results = sorted(results, key= lambda q: q['timestamp'], reverse=True)
    return jsonify({"message" : "Entries retrieved succesfully", "entries" : sorted_results}), 200

@app.route('/get_friends', methods = ["POST"])
@require_jwt
def get_friends(id, data):
    result = db.get_friends(id)
    return jsonify({"message" : "Friends retrieved", 'friends' : result}), 200

@app.route('/send_friend_request', methods = ["POST"])
@require_jwt
def send_friend_request(id, data):
        result = db.send_friend_request(id, data['friend_name'])

        if result:
            return jsonify({"message" : "Request sent"}), 200
        return jsonify({"message" : "Username not found"}), 404

@app.route('/get_requests', methods = ['POST'])
@require_jwt
def get_requests(id, data):
    results = db.get_requests(id)
    return jsonify({"message" : "Returning user friend requests", 'requests' :  results}), 200

@app.route('/decline_friend_request', methods = ['POST'])
@require_jwt
def decline_friend_request(id, data):
    if db.decline_friend_request(id, data['friend_name']):
        return jsonify({"message" : "Friend request declined"}), 200
    return jsonify({"message" : "Error in db while declining request"}), 400

@app.route('/accept_friend_request', methods = ['POST'])
@require_jwt
def accept_friend_request(id, data):
    suc, a = db.accept_friend_request(id, data['friend_name'])
    if suc:
        return jsonify({"message" : "Friend request accepted"}), 200
    return jsonify({"message" : "Error in db while accepting request"}), 400


@app.route('/post_comment', methods = ["POST"])
@require_jwt
def post_comment(id, data):
    if db.post_comment(id, data['post_id'], data['text']):
        return jsonify({"message" : "Comment posted"}), 201
    else: return jsonify({"message" : "Comment too short"}), 400

@app.route('/get_comments', methods = ["POST"])
@require_jwt
def get_comments(id, data):
    comments = db.get_comments(id, data['entry_id'])
    if not comments:
        return jsonify({"comments" : [], "message" : "Not the author of the original post"}), 200
    return jsonify({"comments" : comments, "message" : "Returning comments"}), 200

@app.route('/get_post_with_title', methods = ["POST"])
@require_jwt
def get_post_with_title(id, data):
    return jsonify({"post" : db.get_post_with_title(data['entry_id'])}), 200

@app.route('/get_schedule', methods = ["POST"])
@require_jwt    
def get_schedule(id, data):
    fixed_tasks_json = data['fixed_tasks_json']
    daily_notes = data['daily_notes']
    profile = db.get_user_profile(id) 
    if not profile(): return jsonify({"message" : "User pfoile does not exist or cant be accessed in db"}) 
    return jsonify({"message" : "returning user profile", "profile" : llmcaller.schedule_day(daily_notes,
                    profile['summary'], fixed_tasks_json, profile['wake_time'], profile['sleep_time'], profile['activities'])}) 


@app.route('/create_user_profile', methods = ["POST"])
@require_jwt
def create_user_profile(id, data):
    if(db.create_user_profile(data, id)): return jsonify({"message" : "successfully created your profile"}), 200
    return jsonify({"message" : "erroe while creating profile"}), 400