import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT",3306))
}

class BotDatabase:
    def __init__(self):
        self.conn = None
        self.message = ""

    def connect(self):
        """Establishes the connection to the MySQL database."""
        try:
            self.conn = mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
                port=DB_CONFIG["port"]
            )
            
            if self.conn.is_connected():
                self.message = "Connection Established Successfully"
                print(self.message)
                return 1
            else:
                self.message = "Connection not Established"
                print(self.message)
                return 0  
        except Error as e:
            self.message = f"Error while connecting to MySQL: {e}"
            print(self.message)
            return 0

    def clear(self):
        """Truncates the chat_history table cleanly."""
        if self.connect():
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute("TRUNCATE TABLE chat_history;")
                    self.conn.commit()
                return "Your Past Conversation is Cleared Successfully from the database!"
            except Exception as e:
                # Fixed order: Update the message attribute BEFORE returning
                self.message = f"Truncate error: {e}"
                return "Failed to clear history from the database."
            finally:
                # Use your native class method for a safe, managed teardown
                self.close()
        else:
            return "Failed to connect to the database to clear history."
    
    def close(self):
        """Safely closes the database connection."""
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("MySQL connection closed.")
        else:
            print("No active connection to close.")