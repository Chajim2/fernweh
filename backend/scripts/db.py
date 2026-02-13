import sqlite3
from datetime import datetime
from scripts.db_utils import get_db
from argon2 import PasswordHasher, exceptions

class DiaryDatabase:
    def __init__(self):
        self.create_tables()
        self.ph = PasswordHasher()

    def check_login(self, username, password):
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, password FROM users
                WHERE username = ?
            ''', (username,))
            result = cursor.fetchone()

            if result:
                user_id, hashed_password = result
                try:
                    self.ph.verify(hashed_password, password)
                    return [(user_id,)]
                except exceptions.VerifyMismatchError:
                    return []
            return []

        except sqlite3.Error as e:
            print(f"Database error during login: {e}")
            return []

    def find_user_id(self, username):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM users
            WHERE username = ?
        ''', (username,))
        result = cursor.fetchone()
        if result: return result[0]
        return -1

    def username_taken (self, username):
        conn = get_db()
        cursor = conn.cursor()
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
        conn = get_db()
        cursor = conn.cursor()
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
            timestamp DATETIME NOT NULL,
            FOREIGN KEY (author_id) REFERENCES users(id),
            FOREIGN KEY (post_id) REFERENCES diary_entries(id)
        )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            summary TEXT,
            wake_time TEXT NOT NULL,
            sleep_time TEXT NOT NULL,
            activities TEXT,
            lock_meter REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
            )
            ''')

        conn.commit()

    def save_entry(self, text, emotions, user_id):
        try:
            conn = get_db()
            cursor = conn.cursor()
            timestamp = datetime.now()
            cursor.execute('''
            INSERT INTO diary_entries (authorid, text, timestamp)
            VALUES (?, ?, ?)
            ''', (user_id, text, timestamp))

            entry_id = cursor.lastrowid
            for emotion in emotions:
                cursor.execute('''
                INSERT INTO entry_emotions (entry_id, emotion)
                VALUES (?, ?)
                ''', (entry_id, emotion))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error while saving entry: {e}")
            return False

    def add_friend(self, friend_name, user_id):
        conn = get_db()
        cursor = conn.cursor()
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

        conn.commit()
        return 2

    def get_all_entries(self, user_id):
        conn = get_db()
        cursor = conn.cursor()

        # Get entries with a type indicator
        cursor.execute('''
        SELECT
            diary_entries.id,
            diary_entries.text,
            diary_entries.timestamp,
            GROUP_CONCAT(entry_emotions.emotion) as emotions,
            'post' as type,
            diary_entries.authorid
        FROM diary_entries
        LEFT JOIN entry_emotions ON diary_entries.id = entry_emotions.entry_id
        WHERE diary_entries.authorid = ?
        GROUP BY diary_entries.id

        UNION ALL

        -- Get comments on user's posts
        SELECT
            c.post_id as id,
            c.text,
            c.timestamp,
            NULL as emotions,
            'comment' as type,
            c.author_id as authorid
        FROM comments c
        JOIN diary_entries d ON c.post_id = d.id
        WHERE d.authorid = ?
        ORDER BY timestamp DESC
        ''', (user_id, user_id))

        entries = cursor.fetchall()

        formatted_entries = []
        for entry in entries:
            entry_id, text, timestamp, emotions, entry_type, author_id = entry

            # Get username for both posts and comments
            cursor.execute('SELECT username FROM users WHERE id = ?', (author_id,))
            username = cursor.fetchone()[0]

            if entry_type == 'post':
                emotions_list = emotions.split(',') if emotions else []
                formatted_entries.append({
                    'id': entry_id,
                    'text': text,
                    'timestamp': timestamp,
                    'emotions': emotions_list,
                    'type': 'post',
                    'username': username
                })
            else:  # comment
                formatted_entries.append({
                    'id': entry_id,  # This is the post_id for the post the comment is under (hopefully lol)
                    'text': text,
                    'timestamp': timestamp,
                    'type': 'comment',
                    'username': username

                })

        return formatted_entries


    def get_friends(self, user_id):
        conn = get_db()
        cursor = conn.cursor()
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

    def get_post_with_title(self, entry_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                de.id,
                de.text,
                de.timestamp,
                u.username,
                GROUP_CONCAT(ee.emotion) as emotions
            FROM diary_entries AS de
            JOIN users AS u ON de.authorid = u.id
            LEFT JOIN entry_emotions AS ee ON de.id = ee.entry_id
            WHERE de.id = ?
            GROUP BY de.id
        ''', (entry_id,))

        result = cursor.fetchone()

        if result:
            post_id, text, timestamp, username, emotions_str = result

            return {
                "id": post_id,
                "author": username,
                "text": text,
                "timestamp": timestamp,
                "title": emotions_str
            }

        return None

    def add_user(self, username, password):
        conn = get_db()
        cursor = conn.cursor()

        hashed = self.ph.hash(password)

        cursor.execute('''
            INSERT INTO users(username, password)
            VALUES
                (?, ?)
        ''', (username, hashed))
        conn.commit()

    def remove_friend_request(self, user_id, friend_id):
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM friend_requests
            WHERE user_id = ?
            AND friend_id = ?
        ''', (friend_id, user_id)) #possible issue here, swap the two arguments around
        conn.commit()

    def send_friend_request(self, user_id, friend_name):
        conn = get_db()
        cursor = conn.cursor()
        friend_id = self.find_user_id(friend_name)
        if friend_id == -1: return False
        cursor.execute('''
            INSERT INTO friend_requests(user_id, friend_id)
            VALUES (?, ?)
            ''',
            (int(user_id), int(friend_id))
        )
        conn.commit()
        return True

    def get_requests(self, user_id):
        conn = get_db()
        cursor = conn.cursor()
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
        conn = get_db()
        cursor = conn.cursor()
        if len(text) < 1:
            return False
        timestamp = datetime.now()
        cursor.execute('''
            INSERT INTO comments(author_id, post_id, text, timestamp)
            VALUES (?, ?, ?, ?)
            ''',
            (int(author_id), int(post_id), text, timestamp)
        )
        conn.commit()
        return True

    def get_comments(self, user_id, entry_id):
        conn = get_db()
        cursor = conn.cursor()

        # First check if the user is the author of the entry
        cursor.execute('''
        SELECT authorid FROM diary_entries
        WHERE id = ?
        ''', (user_id,))

        entry_author = cursor.fetchone()

        # If entry doesn't exist or user is not the author, return None
        if not entry_author or entry_author[0] != user_id:
            return False

        cursor.execute('''
        SELECT
            c.id,
            c.text,
            c.author_id,
            u.username as author_name,
            c.timestamp
        FROM comments c
        JOIN users u ON c.author_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.timestamp DESC
        ''', (entry_id,))

        comments = cursor.fetchall()

        # Format the comments
        formatted_comments = []
        for comment in comments:
            formatted_comments.append({
                'id': comment[0],
                'text': comment[1],
                'author_id': comment[2],
                'author_name': comment[3],
                'timestamp': comment[4]
            })

        return formatted_comments

    def get_user_profile(self, user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM user_summaries
        WHERE user_id = ?
        """, (user_id, ))
        data = cursor.fetchone()
        if not data:
            return {}
        formated_profile = {"id": data[1], "summary" : data[2], "wake_time" : data[3], "sleep_time" : data[4], "activities":data[5], "lock_meter":data[6]}
        return formated_profile

    def create_user_profile(self, data, id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_summaries(
            user_id, summary, wake_time,sleep_time, activities, lock_meter)
            VALUES(?, ?, ?, ?, ?, ?)
        """, (id,data['summary'], data['wake_time'], data['sleep_time'], data['activities'], data['lock_meter']))

        conn.commit()
        return True

    def update_user_summary(self, new_summary, id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_summaries SET
            summary = ?
            WHERE user_id = ?
        """, (new_summary, id))

        conn.commit()
        return True

    def close(self):
        conn = get_db()
        conn.close()