"""
SQLite Database Handler
Upgraded database system for persistent storage.
"""

import sqlite3
import json
import os
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any


class Database:
    """SQLite database handler."""
    
    def __init__(self, db_path: str = 'data/bot.db'):
        """Initialize database."""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # User statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                messages INTEGER DEFAULT 0,
                commands_used INTEGER DEFAULT 0,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        
        # Reminders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                reminder_text TEXT NOT NULL,
                reminder_time TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Server settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_settings (
                guild_id INTEGER PRIMARY KEY,
                prefix TEXT DEFAULT '!',
                log_channel_id INTEGER,
                welcome_channel_id INTEGER,
                auto_mod_enabled INTEGER DEFAULT 0,
                settings_json TEXT
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                timezone TEXT,
                preferences_json TEXT
            )
        ''')
        
        # Poll results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS poll_results (
                poll_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                options_json TEXT NOT NULL,
                votes_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                creator_id INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # User Statistics Methods
    def get_user_stats(self, guild_id: int, user_id: int) -> Optional[Dict]:
        """Get user statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM user_stats WHERE guild_id = ? AND user_id = ?',
            (guild_id, user_id)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_user_stats(self, guild_id: int, user_id: int, **kwargs):
        """Update user statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if exists
        stats = self.get_user_stats(guild_id, user_id)
        
        if stats:
            # Update existing
            set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [guild_id, user_id]
            cursor.execute(
                f'UPDATE user_stats SET {set_clause} WHERE guild_id = ? AND user_id = ?',
                values
            )
        else:
            # Insert new
            now = datetime.now(timezone.utc).isoformat()
            fields = ['guild_id', 'user_id', 'first_seen', 'last_seen'] + list(kwargs.keys())
            values = [guild_id, user_id, now, now] + list(kwargs.values())
            placeholders = ', '.join(['?'] * len(values))
            cursor.execute(
                f'INSERT INTO user_stats ({", ".join(fields)}) VALUES ({placeholders})',
                values
            )
        
        conn.commit()
        conn.close()
    
    def increment_message_count(self, guild_id: int, user_id: int):
        """Increment message count for user."""
        stats = self.get_user_stats(guild_id, user_id)
        if stats:
            self.update_user_stats(guild_id, user_id, messages=stats['messages'] + 1)
        else:
            self.update_user_stats(guild_id, user_id, messages=1)
    
    def increment_command_count(self, guild_id: int, user_id: int):
        """Increment command count for user."""
        stats = self.get_user_stats(guild_id, user_id)
        if stats:
            self.update_user_stats(guild_id, user_id, commands_used=stats['commands_used'] + 1)
        else:
            self.update_user_stats(guild_id, user_id, commands_used=1)
    
    # Reminders Methods
    def add_reminder(self, guild_id: int, user_id: int, channel_id: int, 
                     reminder_text: str, reminder_time: datetime):
        """Add a reminder."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reminders 
            (guild_id, user_id, channel_id, reminder_text, reminder_time, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            guild_id, user_id, channel_id, reminder_text,
            reminder_time.isoformat(), datetime.now(timezone.utc).isoformat()
        ))
        
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return reminder_id
    
    def get_due_reminders(self) -> List[Dict]:
        """Get reminders that are due."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            'SELECT * FROM reminders WHERE reminder_time <= ?',
            (now,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_reminder(self, reminder_id: int):
        """Delete a reminder."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
        conn.commit()
        conn.close()
    
    # Server Settings Methods
    def get_server_settings(self, guild_id: int) -> Dict:
        """Get server settings."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM server_settings WHERE guild_id = ?',
            (guild_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            settings = dict(row)
            if settings.get('settings_json'):
                settings.update(json.loads(settings['settings_json']))
            return settings
        return {}
    
    def update_server_settings(self, guild_id: int, **kwargs):
        """Update server settings."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Separate JSON settings
        json_fields = ['settings_json']
        regular_fields = {k: v for k, v in kwargs.items() if k not in json_fields}
        json_settings = {k: v for k, v in kwargs.items() if k in json_fields}
        
        if json_settings:
            regular_fields['settings_json'] = json.dumps(json_settings)
        
        if regular_fields:
            # Check if exists
            cursor.execute(
                'SELECT guild_id FROM server_settings WHERE guild_id = ?',
                (guild_id,)
            )
            
            if cursor.fetchone():
                # Update
                set_clause = ', '.join([f"{k} = ?" for k in regular_fields.keys()])
                values = list(regular_fields.values()) + [guild_id]
                cursor.execute(
                    f'UPDATE server_settings SET {set_clause} WHERE guild_id = ?',
                    values
                )
            else:
                # Insert
                fields = ['guild_id'] + list(regular_fields.keys())
                values = [guild_id] + list(regular_fields.values())
                placeholders = ', '.join(['?'] * len(values))
                cursor.execute(
                    f'INSERT INTO server_settings ({", ".join(fields)}) VALUES ({placeholders})',
                    values
                )
        
        conn.commit()
        conn.close()

