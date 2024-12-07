import os

import streamlit as st

from main import handle_query, update_knowledge_base

def main():
    st.title("Chatbot")

    st.sidebar.header("Upload Files")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'csv'],
        help="Upload PDF, DOCX or CSV files"
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

        st.session_state.file_type = file_extension
        st.session_state.temp_file_path = temp_file_path

        if 'messages' not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a query"):
            if not hasattr(st.session_state, 'file_type'):
                st.error("Please upload a file first.")
                return
            current_file_type = st.session_state.file_type
            try:
                response = handle_query(prompt, current_file_type)
            except Exception as e:
                response = f"An error occured: {str(e)}"
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.write(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.write(response)

if __name__ == "__main__":
    main()