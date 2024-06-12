import mysql.connector
import streamlit as st
import re
from dbconnect import connect_to_database
import bcrypt

def insert_user(email, username, matricNo, university, password):
    conn = None
    cursor = None
    try:
        # Connect to the database
        conn = connect_to_database()
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Define the insert statement
        sql = "INSERT INTO tbl_users(email, username, matricno, university, password) VALUES (%s, %s, %s, %s, %s)"
        data = (email, username, matricNo, university, hashed_password)
        cursor.execute(sql, data)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        print("Exception:", e)
        return False
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def fetch_emails_and_usernames():
    conn = None
    cursor = None
    users_data = []
    
    try:
        # Connect to the database
        conn = connect_to_database()  # Implement this function in your 'dbconnect' module
        cursor = conn.cursor(dictionary=True)
        
        # Execute the query to fetch email and username
        cursor.execute("SELECT email, username FROM tbl_users")
        
        # Fetch all the rows
        users_data = cursor.fetchall()
        
    except mysql.connector.Error as e:
        print(f"Error reading data from MySQL table: {e}")
        
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return users_data

def sign_up():
    # Initialize variables to store user input
    email = ""
    username = ""
    matricNo = ""
    university = ""
    password1 = ""
    password2 = ""

    with st.form(key='signup', clear_on_submit=True):
        st.subheader(':green[Sign Up]')
        email = st.text_input('Email', placeholder='Please enter your email')
        username = st.text_input('Username', placeholder='Please enter your username')
        matricNo = st.text_input('Matric No', placeholder='Please enter your matric no')
        university = st.text_input('University', placeholder='Please enter your university')
        password1 = st.text_input('Password', type='password', placeholder='Please enter your password')
        password2 = st.text_input('Confirm Password', type='password', placeholder='Please confirm your password')

        if st.form_submit_button('Sign Up'):
            if not email:
                st.error('Email is required.')
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error('Invalid email format.')
            elif not username:
                st.error('Username is required.')
            elif not re.match(r'^[a-z]+$', username):
                st.error('Username must only contain lowercase letters.')
            elif not matricNo:
                st.error('Matric No is required.')
            elif not university:
                st.error('University is required.')
            elif not password1:
                st.error('Password is required.')
            elif password1 != password2:
                st.error('Passwords do not match.')
            else:
                # Fetch existing emails and usernames from the database
                existing_data = fetch_emails_and_usernames()
                
                # Check if email or username already exists
                email_exists = any(entry['email'] == email for entry in existing_data)
                username_exists = any(entry['username'] == username for entry in existing_data)
                
                if email_exists:
                    st.error('Email already exists. Please use a different email.')
                elif username_exists:
                    st.error('Username already exists. Please choose a different username.')
                else:
                    # Call function to insert user into the database
                    insert_result = insert_user(email, username, matricNo, university, password2)
                    
                    # Initialize variables to store user input
                    email = ""
                    username = ""
                    matricNo = ""
                    university = ""
                    password1 = ""
                    password2 = ""
                    
                    if insert_result:
                        print(insert_result)
                        st.success('User successfully created!')
                    else:
                        st.error('Failed to create user.')

