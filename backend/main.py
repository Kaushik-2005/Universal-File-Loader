import os
from dotenv import load_dotenv
from general_chatbot import EnhancedDocumentChatbot

load_dotenv()

# Global chatbot instance
chatbot = EnhancedDocumentChatbot()


def update_knowledge_base(file_path, file_type):
    """
    Update knowledge base for a specific file

    :param file_path: Path to the uploaded file
    :param file_type: Type of the file (pdf, csv, docx)
    :return: Status message
    """
    try:
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Use the enhanced chatbot's method to update knowledge base
        return chatbot.update_knowledge_base(file_path)

    except Exception as e:
        print(f"Error updating knowledge base: {str(e)}")
        raise


def handle_query(question, file_type=None):
    """
    Handle query based on file type or general conversation

    :param question: User's query
    :param file_type: Optional file type context
    :return: AI's response
    """
    try:
        # Get response from the enhanced chatbot
        response = chatbot.get_response(question, file_type)
        return response

    except Exception as e:
        return f"An error occurred while processing your query: {str(e)}"


def main():
    """
    Main interaction loop for document query assistant
    """
    while True:
        file_path = input("Enter the path to the file (PDF, CSV, or DOCX, or 'skip' for general chat): ")

        if file_path.lower() == 'skip':
            break

        if os.path.exists(file_path):
            try:
                result = update_knowledge_base(file_path, None)
                print(result)
                break
            except Exception as e:
                print(f"An error occurred: {str(e)}")
        else:
            print("File not found. Please check the file path and try again.")

    while True:
        question = input("Enter your question (or 'exit' to quit): ")

        if question.lower() == "exit":
            break

        response = handle_query(question)
        print("\nResponse from LLM:", response)
        print("\n" + "-" * 50)


if __name__ == "__main__":
    main()