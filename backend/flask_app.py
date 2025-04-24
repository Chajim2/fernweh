from flask import Flask, request, jsonify
from scripts.db import DiaryDatabase
from scripts.ai import LLMCaller
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
db = DiaryDatabase()

llmcaller = LLMCaller()

@app.route('/')
def hello_world():
    return "Nun to see here friend"

@app.route('/get_emotions', methods = ["POST"])
def get_emotions():
    if request.method == "POST":
        data = request.get_json()
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
            return jsonify({"message" : "Successfull login", "id" : users_found[0][0]}), 200

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

@app.route('/add_friend', methods = ['POST'])
def add_friend():
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return jsonify({"message" : "Invalid JSON"}), 400

        result = db.add_friend(data['friend_name'], data['id'])

        if result == 0:
            return jsonify({"message" : "Friend not found"}), 404

        if result == 1:
            return jsonify({"message" : "Already friends"}), 409

        return jsonify({'message' : "Friend added successfully"}), 201

@app.route('/save_entry', methods = ['POST'])
def save_entry():
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return jsonify({"message" : "No data sent"}), 400

        if db.save_entry(data['text'], data['emotions'], data['id']):
            return jsonify({"message": "Entry saved"}), 201
        else:
            return jsonify({"message": "Error while trying to save entry"}), 400

@app.route ('/get_all_entries', methods = ["POST"])
def get_all_entries():
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        results = db.get_all_entries(data['id'])
        return jsonify({"message" : "Entries retrieved succesfully", "entries" : results}), 200

@app.route('/get_friends', methods = ["POST"])
def get_friends():
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        result = db.get_friends(data['id'])
        return jsonify({"message" : "Friends retrieved", 'friends' : result}), 200

@app.route('/send_friend_request', methods = ["POST"])
def send_friend_request():
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        result = db.send_friend_request(data['id'], data['friend_name'])

        if result:
            return jsonify({"message" : "Request sent"}), 200
        return jsonify({"message" : "Username not found"}), 404

@app.route('/get_requests', methods = ['POST'])
def get_requests():
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        results = db.get_requests(data['id'])
        return jsonify({"message" : "Returning user friend requests", 'requests' :  results}), 200

@app.route('/decline_friend_request', methods = ['POST'])
def decline_friend_request():
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        if db.decline_friend_request(data['id'], data['friend_name']):
            return jsonify({"message" : "Friend request declined"}), 200
        return jsonify({"message" : "Error in db while declining request"}), 400

@app.route('/accept_friend_request', methods = ['POST'])
def accept_friend_request():
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        suc, a = db.accept_friend_request(data['id'], data['friend_name'])
        if suc:
            return jsonify({"message" : "Friend request accepted", "xd" : a}), 200
        return jsonify({"message" : "Error in db while accepting request"}), 400


@app.route('/post_comment', methods = ["POST"])
def post_comment():
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        if db.post_comment(data['user_id'], data['post_id'], data['text']):
            return jsonify({"message" : "Comment posted"}), 201
        else: return jsonify({"message" : "Comment too short"}), 400

@app.route('/get_comments', methods = ["POST"])
def get_comments():
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return jsonify({"message" : "No data sent"}), 400
        comments = db.get_comments(data['user_id'], data['entry_id'])
        if not comments:
            return jsonify({"comments" : [], "message" : "Not the author of the original post"}), 200
        return jsonify({"comments" : comments, "message" : "Returning comments"}), 200
