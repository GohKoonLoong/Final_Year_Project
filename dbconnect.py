import mysql.connector
from dotenv import load_dotenv
import os


def connect_to_database():
    load_dotenv()
    # Connect to MySQL database
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    return conn

