import streamlit as st
import whisper
import tempfile
from streamlit_mic_recorder import mic_recorder
import langcodes as lc
import os
import subprocess

# Disable tokenizers parallelism to avoid warnings
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

st.set_page_config(page_title="Audio Processing and Q&A", page_icon="🔊")
st.header("Upload Your Recording 🔊")

username = st.session_state.get('username', "")
print(username)

if username == "":
    st.warning("Please login to chat with the Personal Assistant")
else:
    audio_file = st.file_uploader("Upload an audio file", type=["wav","mp3","ogg"])

    # Function to check if ffmpeg is installed
    def check_ffmpeg():
        try:
            subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
            return True
        except FileNotFoundError:
            return False

    # Function to process audio and display results
    def process_audio_file(file_path, task_option):
        if task_option == "Transcribe":
            result = model.transcribe(file_path)
        elif task_option == "Translate":
            result = model.transcribe(file_path, task="translate")
        
        detected_language_code = result["language"]
        detected_language_name = lc.get(detected_language_code).display_name()
        st.success(f"Detected language: {detected_language_name} ({detected_language_code})")
        st.markdown(result["text"])

    if audio_file is not None:
        if check_ffmpeg():
            model = whisper.load_model("base")
            print("Whisper Model Loaded")
            st.audio(audio_file)

            task_option = st.selectbox("Choose task", ("Transcribe", "Translate"))

            if st.button("Process Audio"):
                with st.spinner(f"{task_option} Audio"):
                    # Save the uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                        temp_audio_file.write(audio_file.read())
                        temp_audio_file_path = temp_audio_file.name
                    
                    process_audio_file(temp_audio_file_path, task_option)
                    os.remove(temp_audio_file_path)
        else:
            st.error("ffmpeg is not installed. Please install ffmpeg and try again.")
    else:
        st.error("Please upload an audio file")

