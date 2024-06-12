import streamlit as st
import base64
import requests
from streamlit_chat import message
from dotenv import load_dotenv
import os
from langchain.schema import HumanMessage, AIMessage

load_dotenv()

# OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")

# Function to encode the image to base64
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# Function to handle image and question using GPT-4 vision
def handle_image(image_bytes, user_message):
    base64_image = encode_image(image_bytes)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

def main():
    st.set_page_config(page_title="Image Handler", page_icon="🖼️")

    username = st.session_state.get('username', "")
    print(username)
    
    # Initialize prefixed session state variables
    if "image_handler_messages" not in st.session_state:
        st.session_state.image_handler_messages = []

    st.header("Image Handler 🖼️")

    if username == "":
        st.warning("Please login to chat with the Personal Assistant")
    else:
        
        uploaded_image = st.file_uploader("Upload an image file", type=["jpg", "jpeg", "png"])

        if uploaded_image is not None:
            st.image(uploaded_image, caption='Uploaded Image', use_column_width=True)
            
        user_question = st.chat_input("Describe your image or ask a question about it:",disabled=not uploaded_image)

        if user_question:
            st.session_state.image_handler_messages.append(HumanMessage(content=user_question))
            with st.spinner("Processing image..."):
                response = handle_image(uploaded_image.getvalue(), user_question)
                st.session_state.image_handler_conversation = response  # Set the conversation state
                st.session_state.image_handler_messages.append(AIMessage(content=response["choices"][0]["message"]["content"]))

            for i, msg in enumerate(st.session_state.image_handler_messages):
                if isinstance(msg, HumanMessage):
                    message(msg.content, is_user=True, key=str(i) + '_user')
                else:
                    message(msg.content, is_user=False, key=str(i) + '_ai')

if __name__ == '__main__':
    main()
