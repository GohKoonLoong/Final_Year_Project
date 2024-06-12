import streamlit as st
import streamlit_authenticator as stauth
import mysql.connector
from dbconnect import connect_to_database
from signup import sign_up

@st.cache_data
def fetch_users():
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM tbl_users")
        users = cursor.fetchall()
    except mysql.connector.Error as e:
        st.error(f"Error reading data from MySQL table: {e}")
    finally:
        cursor.close()
        conn.close()
    return users

def main():
    st.set_page_config(page_title="Login")
    users = fetch_users()
    usernames = [user['username'] for user in users]
    credentials = {'usernames': {}}
    for index, username in enumerate(usernames):
        credentials['usernames'][username] = {'name': users[index]['email'], 'password': users[index]['password']}

    Authenticator = stauth.Authenticate(credentials, cookie_name='Streamlit', key='abcdef', cookie_expiry_days=4)
    email, authentication_status, username = Authenticator.login(fields=[':green[Login]', 'main'])

    if authentication_status:
        st.session_state.user = username
        st.subheader(f'Welcome {username}')
        Authenticator.logout('Log Out')
    elif authentication_status is False:
        st.error("Username or password is incorrect")
        print(username);
        sign_up()
    elif authentication_status is None:
        sign_up()

if __name__ == '__main__':
    main()
