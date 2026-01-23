import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_db():
    """
    Create and return a MySQL database connection
    Uses environment variables for credentials:
    - DB_HOST: Database host (default: localhost)
    - DB_USER: Database user (default: root)
    - DB_PASSWORD: Database password (default: empty)
    - DB_NAME: Database name (default: ruang_hijau)
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'root'),
            database=os.getenv('DB_NAME', 'ruang_hijau'),
            autocommit=False,
            raise_on_warnings=False
        )
        return connection
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(f"Database connection error: {err}")
        raise
