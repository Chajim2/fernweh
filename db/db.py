import sqlite3
from datetime import datetime
from utils.loading import resource_path, UserState

class DiaryDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(resource_path('db/diary_entries.db'))
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
        ''')
        
        # Create diary entries table with user_id
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS diary_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
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
        
        # Create friendships table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS friendships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (friend_id) REFERENCES users (id)
        )
        ''')
        
        self.conn.commit()

    def save_entry(self, text, emotions):
        user_id = UserState.get_user_id()
        cursor = self.conn.cursor()
        timestamp = datetime.now()
        
        cursor.execute('''
        INSERT INTO diary_entries (user_id, text, timestamp)
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

    def get_all_entries(self):
        user_id = UserState.get_user_id()
        cursor = self.conn.cursor()
        
        # Get entries with their emotions for specific user
        cursor.execute('''
        SELECT 
            diary_entries.id,
            diary_entries.text,
            diary_entries.timestamp,
            GROUP_CONCAT(entry_emotions.emotion) as emotions
        FROM diary_entries
        LEFT JOIN entry_emotions ON diary_entries.id = entry_emotions.entry_id
        WHERE diary_entries.user_id = ?
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

    def close(self):
        self.conn.close()