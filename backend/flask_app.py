from flask import Flask, request, jsonify
from scripts.db import DiaryDatabase
from scripts.ai import LLMCaller
import logging
import jwt
from jwt import InvalidTokenError
from functools import wraps
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
db = DiaryDatabase()

llmcaller = LLMCaller()

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-secret-key')  # Fallback to default if not set
ALGORITHM = 'HS256'

def require_jwt(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()

        if not data or 'id' not in data:
            return jsonify({'error': 'JWT is missing in request body'}), 401
        
        token = data['id']
        print(token)

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return f(*args, **kwargs, id=payload['id'], data=data)
        
        except InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    
    return decorated_function

def create_jwt(payload_data):
    payload = payload_data.copy()

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token

@app.route('/')
def hello_world():
    return "Nun to see here friend"

@app.route('/get_emotions', methods = ["POST"])
@require_jwt
def get_emotions(id, data):
    if request.method == "POST":
        if data is None:
            return jsonify({"message": "Invalid JSON"}), 400

        emotions = llmcaller.call_llm(data['text'])
        formated_emotions = []
        for line in emotions.split(";"):
            emotion, description = line.split(":")
            formated_emotions.append({"emotion" : emotion, "description" : description})
        return jsonify({"emotions": formated_emotions, "message" : "Worked"}), 200


@app.route('/login', methods = ['POST'])
def login():
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return jsonify({"message": "Invalid JSON"}), 400

        username, password = data['username'], data['password']
        users_found = list(db.check_login(username, password))
        if len(users_found) == 0:
            return jsonify({"message": "User not found"}), 404
        else:
            token = create_jwt({'id': users_found[0][0]})
            return jsonify({"message" : "Successfull login", "id" : token}), 200

@app.route('/register', methods = ['POST'])
def register():
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return jsonify({"message" : "Invalid JSON"}), 400

        username, password = data['username'], data['password']
        if db.username_taken(username):
            return jsonify({"message": "Username taken"}), 409
        else:
            db.add_user(username, password)
            return jsonify({"message": "User added successfully"}), 201

@app.route('/save_entry', methods = ['POST'])
@require_jwt
def save_entry(id, data):
    if request.method == "POST":
        if data is None:
            return jsonify({"message" : "No data sent"}), 400

        if db.save_entry(data['text'], data['emotions'], id):
            return jsonify({"message": "Entry saved"}), 201
        else:
            return jsonify({"message": "Error while trying to save entry"}), 400

@app.route ('/get_all_entries', methods = ["POST"])
@require_jwt
def get_all_entries(id, data):
    if request.method == "POST":
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        results = db.get_all_entries(id)
        return jsonify({"message" : "Entries retrieved succesfully", "entries" : results}), 200

@app.route('/get_friends', methods = ["POST"])
@require_jwt
def get_friends(id, data):
    if request.method == "POST":
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        result = db.get_friends(id)
        return jsonify({"message" : "Friends retrieved", 'friends' : result}), 200

@app.route('/send_friend_request', methods = ["POST"])
@require_jwt
def send_friend_request(id, data):
    if request.method == "POST":
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        result = db.send_friend_request(id, data['friend_name'])

        if result:
            return jsonify({"message" : "Request sent"}), 200
        return jsonify({"message" : "Username not found"}), 404

@app.route('/get_requests', methods = ['POST'])
@require_jwt
def get_requests(id, data):
    if request.method == "POST":
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        results = db.get_requests(id)
        return jsonify({"message" : "Returning user friend requests", 'requests' :  results}), 200

@app.route('/decline_friend_request', methods = ['POST'])
@require_jwt
def decline_friend_request(id, data):
    if request.method == "POST":
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        if db.decline_friend_request(id, data['friend_name']):
            return jsonify({"message" : "Friend request declined"}), 200
        return jsonify({"message" : "Error in db while declining request"}), 400

@app.route('/accept_friend_request', methods = ['POST'])
@require_jwt
def accept_friend_request(id, data):
    if request.method == "POST":
        if data is None:
            return jsonify({"message" : "No data sent"}), 400

        friend_requests = db.get_requests(id)
        friend_id = db.find_user_id(data['friend_name'])

        if friend_id not in friend_requests:
            return jsonify({"message" : "Friend request does not exist"}), 400

        suc, a = db.accept_friend_request(id, data['friend_name'])

        if suc:
            return jsonify({"message" : "Friend request accepted", "xd" : a}), 200
        return jsonify({"message" : "Error in db while accepting request"}), 400


@app.route('/post_comment', methods = ["POST"])
@require_jwt
def post_comment(id, data):
    if request.method == "POST":
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        if db.post_comment(id, data['post_id'], data['text']):
            return jsonify({"message" : "Comment posted"}), 201
        else: return jsonify({"message" : "Comment too short"}), 400

@app.route('/get_comments', methods = ["POST"])
@require_jwt
def get_comments(id, data):
    if request.method == "POST":
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        comments = db.get_comments(id, data['entry_id'])
        if not comments:
            return jsonify({"comments" : [], "message" : "Not the author of the original post"}), 200
        return jsonify({"comments" : comments, "message" : "Returning comments"}), 200
