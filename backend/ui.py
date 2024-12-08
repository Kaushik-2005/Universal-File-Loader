import os
import streamlit as st
from main import handle_query, update_knowledge_base
from db import FBDB

# Initialize Firebase
service_account_key_path = "service_account_key_path.json"
firebase_db = FBDB(service_account_key_path)

USER_ID = "streamlit_user"  # Unique user ID for the conversation

def load_messages_from_firebase():
    """
    Load messages from Firebase for the current user.
    """
    messages = firebase_db.get(USER_ID)
    if messages:
        st.session_state.messages = messages
    else:
        st.session_state.messages = []

def store_messages_to_firebase():
    """
    Store current messages to Firebase for the current user.
    """
    firebase_db.update(USER_ID, st.session_state.messages)

def main():
    st.title("Chatbot")

    # Initialize session state if not already initialized
    if 'messages' not in st.session_state:
        load_messages_from_firebase()
    if 'file_type' not in st.session_state:
        st.session_state.file_type = None
    if 'temp_file_path' not in st.session_state:
        st.session_state.temp_file_path = None

    # Sidebar for file upload
    st.sidebar.header("Upload Files")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'csv'],
        help="Upload PDF, DOCX, or CSV files"
    )

    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        temp_file_path = os.path.join("temp", uploaded_file.name)
        os.makedirs("temp", exist_ok=True)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        try:
            update_result = update_knowledge_base(temp_file_path, file_extension)
            st.sidebar.success(update_result)
        except Exception as e:
            st.sidebar.error(f"Error updating knowledge base: {str(e)}")

        # Update session state with file information
        st.session_state.file_type = file_extension
        st.session_state.temp_file_path = temp_file_path

    # Display conversation messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Text input always visible
    prompt = st.chat_input("Ask a query")

    if prompt:
        # Process the query and return a response
        current_file_type = st.session_state.file_type
        try:
            # Handle query based on the file type
            response = handle_query(prompt, current_file_type)
        except Exception as e:
            response = f"An error occurred: {str(e)}"

        # Append user and assistant messages
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

        # Store the updated messages to Firebase
        store_messages_to_firebase()

if __name__ == "__main__":
    main()