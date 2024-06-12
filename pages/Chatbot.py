import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
import os
import csv
from streamlit_mic_recorder import mic_recorder
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# Initialize Streamlit session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are a personal assistant that helps university students in their learning journey")
    ]

# File path to save chat history
CHAT_HISTORY_FILE = "storage/chat_history.csv"

def init():
    load_dotenv()
    if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
        print("OPENAI_API_KEY is not set")
        exit(1)
    else:
        print("OPENAI_API_KEY is set")

def save_chat_history_to_file(username, messages):
    with open(CHAT_HISTORY_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "User"
            elif isinstance(msg, AIMessage):
                role = "Bot"
            else:
                continue
            writer.writerow([username, role, msg.content])

def retrieve_chat_history_from_file(username):
    if not os.path.exists(CHAT_HISTORY_FILE):
        return []
    chat_history = []
    with open(CHAT_HISTORY_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username:
                role, content = row[1], row[2]
                chat_history.append((role, content))
    return chat_history

def main():
    init()
    
    # Authenticate user and retrieve username from session state
    username = st.session_state.get('username', "")
    print(username)
    
    chat = ChatOpenAI(temperature=0)
    
    st.header("Learning Personal Assistant 🤖")
    
    user_input = st.chat_input("Your messages: ", key="user_input", disabled=not username)
    
    if username == "":
        st.warning("Please login to chat with the Personal Assistant")

    if user_input:
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("Thinking...."):
            response = chat.invoke(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=response.content))
        
        # Save chat history to file
        save_chat_history_to_file(username, [HumanMessage(content=user_input), AIMessage(content=response.content)])
    
    # Retrieve chat history from file based on username
    chat_history = retrieve_chat_history_from_file(username)
    print("Chat History:", chat_history)
    
    # Display chat history as conversation
    for i, (role, content) in enumerate(chat_history):
        if role == "User":
            message(content, is_user=True, key=str(i) + '_user')
        elif role == "Bot":
            message(content, is_user=False, key=str(i) + '_ai')

if __name__ == '__main__':
    main()
