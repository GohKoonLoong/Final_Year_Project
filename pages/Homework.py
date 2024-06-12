import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
# from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from streamlit_chat import message

import os


# Disable tokenizers parallelism to avoid warnings
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks
    
def get_vectorstore(text_chunks):
    if text_chunks:
        # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        return vectorstore
    else:
        st.error("No text chunks found. Please ensure that the uploaded PDF documents contain text.")


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def handle_userinput(user_question):
    if st.session_state.conversation:
        response = st.session_state.conversation.invoke({'question': user_question})
        st.session_state.chat_history = response['chat_history']
        with st.spinner("Thinking"):
            for i, msg in enumerate(st.session_state.chat_history):
                if i % 2 == 0:
                    message(msg.content, is_user=True, key=str(i) + '_user')
                else:
                    message(msg.content, is_user=False, key=str(i) + '_ai')
    else:
        st.error("Please input file to have conversation.")

             
    
def main():
    
    username = st.session_state.get('username', "")
    print(username)
    
    load_dotenv()
    st.set_page_config(page_title="Homework Uploading", page_icon=":books:")
    
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
        
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    
    st.header("Homework Uploading :books:")
    
    if username == "":
        st.warning("Please login to chat with the Personal Assistant")
    else:
        pdf_docs = st.file_uploader("Upload your homework here and click on Process", accept_multiple_files=True,type="pdf")
        
        if st.button("Process"):
            if pdf_docs:  # Check if any files are uploaded
                with st.spinner("Processing"):
                    #get pdf text
                    raw_text = get_pdf_text(pdf_docs)
                    
                    #get the text chunks
                    text_chunks = get_text_chunks(raw_text)
                    
                    #create vector store
                    vectorstore = get_vectorstore(text_chunks)
                    
                    #create conversation chain
                    if vectorstore:  # Check if vectorstore is not None
                        st.session_state.conversation = get_conversation_chain(vectorstore)
                    else:
                        st.error("Failed to create vector store.")
            else:
                st.error("Please upload a file before clicking the Process button.")
        
        user_question = st.chat_input("Ask a question about your homework: ", disabled=not pdf_docs)
        
        if user_question:
            handle_userinput(user_question)
    

                
if __name__ == '__main__':
    main()