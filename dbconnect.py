import mysql.connector

def connect_to_database():
    # Connect to MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        port=3308,
        user="root",
        password="",
        database="fyp_db"
    )
    return conn

