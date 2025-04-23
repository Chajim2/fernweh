import sqlite3
from datetime import datetime

class DiaryDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('database.db', check_same_thread=False)
        self.create_tables()

    def find_user_id(self, username):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id FROM users
            WHERE username = ?
        ''', (username,))
        result = cursor.fetchone()
        if result: return result[0]
        return -1

    def check_login(self, username, password):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                SELECT id FROM users
                WHERE username = ?
                AND password = ?
            ''', (username, password))
            return cursor.fetchall()

        except Exception as e:
            print(f"Database error: {e}")
            return []

    def username_taken (self, username):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                SELECT id FROM users
                WHERE username = ?
            ''', (username, ))
            return cursor.fetchone() is not None

        except Exception as e:
            print(f"Database error: {e}")
            return True


    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diary_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            authorid INTEGER,
            FOREIGN KEY(authorid) REFERENCES users(id)
            )
        ''')

        # Create emotions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entry_emotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER,
            emotion TEXT NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES diary_entries (id)
        )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS friendships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (friend_id) REFERENCES users (id)
        )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (friend_id) REFERENCES users (id)
        )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY (author_id) REFERENCES users(id)
            FOREIGN KEY (post_id) REFERENCES diary_entries
        )
        ''')

        self.conn.commit()

    def save_entry(self, text, emotions, user_id):
        try:
            cursor = self.conn.cursor()
            timestamp = datetime.now()
            cursor.execute('''
            INSERT INTO diary_entries (authorid, text, timestamp)
            VALUES (?, ?, ?)
            ''', (user_id, text, timestamp))

            entry_id = cursor.lastrowid

            # Save the emotions
            for emotion in emotions:
                cursor.execute('''
                INSERT INTO entry_emotions (entry_id, emotion)
                VALUES (?, ?)
                ''', (entry_id, emotion))

            self.conn.commit()
            return True
        except:
            return False

    def add_friend(self, friend_name, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users')
        cursor.execute('''
            SELECT id FROM users
            WHERE username = ?
        ''', (friend_name,))

        result = cursor.fetchone()
        if not result:
            return 0

        friend_id = result[0]

        cursor.execute('''
            SELECT * FROM friendships
            WHERE (user_id = ? AND friend_id = ?)
            OR (user_id = ? AND friend_id = ?)
        ''', (user_id, friend_id, friend_id, user_id))

        if cursor.fetchone():
            return 1

        # Add friendship
        cursor.execute('''
            INSERT INTO friendships (user_id, friend_id)
            VALUES (?, ?)
        ''', (user_id, friend_id))

        self.conn.commit()
        return 2

    def get_all_entries(self, user_id):
        cursor = self.conn.cursor()

        cursor.execute('''
        SELECT
            diary_entries.id,
            diary_entries.text,
            diary_entries.timestamp,
            GROUP_CONCAT(entry_emotions.emotion) as emotions
        FROM diary_entries
        LEFT JOIN entry_emotions ON diary_entries.id = entry_emotions.entry_id
        WHERE diary_entries.authorid = ?
        GROUP BY diary_entries.id
        ORDER BY diary_entries.timestamp DESC
        ''', (user_id,))

        entries = cursor.fetchall()

        # Format the entries
        formatted_entries = []
        for entry in entries:
            emotions = entry[3].split(',') if entry[3] else []
            formatted_entries.append({
                'id': entry[0],
                'text': entry[1],
                'timestamp': entry[2],
                'emotions': emotions
            })

        return formatted_entries


    def get_friends(self, user_id):
        cursor = self.conn.cursor()
        # Get all friends (both where user is user_id and where user is friend_id)
        cursor.execute('''
            SELECT u.id, u.username
            FROM users u
            JOIN friendships f ON (u.id = f.friend_id OR u.id = f.user_id)
            WHERE (f.user_id = ? OR f.friend_id = ?)
            AND u.id != ?
        ''', (user_id, user_id, user_id))

        friends = cursor.fetchall()

        # Format the results
        formatted_friends = []
        for friend in friends:
            formatted_friends.append({
                'id': friend[0],
                'username': friend[1]
            })

        return formatted_friends

    def add_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO users(username, password)
            VALUES
                (?, ?)
        ''', (username, password))
        self.conn.commit()

    def remove_friend_request(self, user_id, friend_id):
        cursor = self.conn.cursor()

        cursor.execute('''
            DELETE FROM friend_requests
            WHERE user_id = ?
            AND friend_id = ?
        ''', (friend_id, user_id)) #possible issue here, swap the two arguments around
        self.conn.commit()

    def send_friend_request(self, user_id, friend_name):
        cursor = self.conn.cursor()
        friend_id = self.find_user_id(friend_name)
        if friend_id == -1: return False
        cursor.execute('''
            INSERT INTO friend_requests(user_id, friend_id)
            VALUES (?, ?)
            ''',
            (int(user_id), int(friend_id))
        )
        self.conn.commit()
        return True

    def get_requests(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT u.username FROM friend_requests fr
            JOIN users u
            ON u.id = fr.user_id
            WHERE fr.friend_id = ?
        ''', (user_id,))
        results = cursor.fetchall()
        return [username[0] for username in results]

    def accept_friend_request(self, user_id, friend_name):
        friend_id = self.find_user_id(friend_name)
        if friend_id == -1: return False
        result = self.add_friend(friend_name, user_id)
        if result in [1,2]:
            xd = self.remove_friend_request(user_id, friend_id)
            return True, xd
        return False

    def decline_friend_request(self, user_id, friend_name):
        friend_id = self.find_user_id(friend_name)
        if friend_id == -1: return False
        self.remove_friend_request(user_id, friend_id)
        return True

    def post_comment(self, author_id, post_id, text):
        cursor = self.conn.cursor()
        if len(text) < 1:
            return False
        cursor.execute('''
            INSERT INTO comments(author_id, post_id, text)
            VALUES (?, ?, ?)
            ''',
            (int(author_id), int(post_id), text)
        )
        self.conn.commit()
        return True

    def get_comments(self, user_id, entry_id):
        cursor = self.conn.cursor()

        # First check if the user is the author of the entry
        cursor.execute('''
        SELECT authorid FROM diary_entries
        WHERE id = ?
        ''', (entry_id,))

        entry_author = cursor.fetchone()

        # If entry doesn't exist or user is not the author, return None
        if not entry_author or entry_author[0] != user_id:
            return False

        cursor.execute('''
        SELECT
            c.id,
            c.text,
            c.author_id,
            u.username as author_name
        FROM comments c
        JOIN users u ON c.author_id = u.id
        WHERE c.post_id = ?
        ''', (entry_id,))

        comments = cursor.fetchall()

        # Format the comments (optional)
        formatted_comments = []
        for comment in comments:
            formatted_comments.append({
                'id': comment[0],
                'text': comment[1],
                'author_id': comment[2],
                'author_name': comment[3]
            })

        return formatted_comments


    def close(self):
        self.conn.close()