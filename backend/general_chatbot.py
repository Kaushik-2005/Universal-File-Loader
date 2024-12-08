import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from loader.pdf_loader import PDFQueryAssistant
from loader.csv_loader import CSVQueryAssistant
from loader.docx_loader import DOCXQueryAssistant

load_dotenv()


class EnhancedDocumentChatbot:
    def __init__(self):
        # Initialize general conversational model
        self.general_model = GoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.7,
            max_tokens=1024
        )

        # File-specific assistants
        self.pdf_assistant = None
        self.csv_assistant = None
        self.docx_assistant = None

        # Supported file types
        self.SUPPORTED_FILE_TYPES = {
            '.pdf': 'pdf',
            '.csv': 'csv',
            '.docx': 'docx'
        }

        # Prompt templates
        self.general_prompt_template = PromptTemplate(
            template="""You are an intelligent AI assistant. Provide a helpful, engaging, and comprehensive response to the following query:

            Query: {query}

            Response:""",
            input_variables=["query"]
        )

        self.file_integrated_prompt_template = PromptTemplate(
            template="""You are an AI assistant with access to both document context and general knowledge. 
            Prioritize answering from the provided context, but supplement with your broader knowledge if needed.

            Document Context:
            {context}

            Query: {query}

            Comprehensive Response:""",
            input_variables=["context", "query"]
        )

    def detect_file_type(self, file_path):
        """
        Automatically detect file type based on extension

        :param file_path: Path to the file
        :return: Detected file type or None if unsupported
        """
        # Get file extension
        file_extension = os.path.splitext(file_path)[1].lower()

        # Check if extension is supported
        return self.SUPPORTED_FILE_TYPES.get(file_extension)

    def update_knowledge_base(self, file_path):
        """
        Update knowledge base by automatically detecting file type
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Detect file type
            file_type = self.detect_file_type(file_path)

            if not file_type:
                raise ValueError(f"Unsupported file type for: {file_path}")

            # Process file based on type
            if file_type == 'pdf':
                self.pdf_assistant = PDFQueryAssistant(file_path)
                self.pdf_assistant.process_pdf()
                return "PDF knowledge base updated successfully."

            elif file_type == 'csv':
                self.csv_assistant = CSVQueryAssistant(file_path)
                self.csv_assistant.process_csv()
                return "CSV knowledge base updated successfully."

            elif file_type == 'docx':
                self.docx_assistant = DOCXQueryAssistant(file_path)
                self.docx_assistant.process_docx()
                return "DOCX knowledge base updated successfully."

        except Exception as e:
            print(f"Error updating knowledge base: {str(e)}")
            raise

    def get_response(self, query, file_type=None):
        """
        Get response based on query and optional file context
        """
        try:
            # File-specific mode
            if file_type:
                file_assistant_map = {
                    'pdf': self.pdf_assistant,
                    'csv': self.csv_assistant,
                    'docx': self.docx_assistant
                }

                file_assistant = file_assistant_map.get(file_type)

                if file_assistant:
                    # Use file-specific response method
                    return file_assistant.get_response(query)
                else:
                    raise ValueError(f"No assistant available for {file_type}")

            # General conversation mode
            else:
                # Use general LLM chain
                general_chain = self.general_prompt_template | self.general_model
                response = general_chain.invoke({"query": query})

                # Get text attribute if it exists, else convert to string
                return response.text if hasattr(response, 'text') else str(response)

        except Exception as e:
            return f"An error occurred while generating response: {str(e)}"


def main():
    chatbot = EnhancedDocumentChatbot()
    print("Enhanced Document Chatbot")
    print("Commands:")
    print("1. Type a question to chat")
    print("2. Type 'upload <file_path>' to upload a document")
    print("3. Type 'exit' to quit")

    while True:
        user_input = input("\nYour input: ")

        if user_input.lower() == 'exit':
            break

        if user_input.startswith('upload'):
            try:
                # Split input and extract file path
                _, file_path = user_input.split(maxsplit=1)

                result = chatbot.update_knowledge_base(file_path)
                print(result)
            except Exception as e:
                print(f"Upload error: {e}")
            continue

        # Determine if a file is currently loaded
        file_type = None
        if chatbot.pdf_assistant or chatbot.csv_assistant or chatbot.docx_assistant:
            if chatbot.pdf_assistant:
                file_type = 'pdf'
            elif chatbot.csv_assistant:
                file_type = 'csv'
            elif chatbot.docx_assistant:
                file_type = 'docx'

        response = chatbot.get_response(user_input, file_type)
        print("\nChatbot:", response)


if __name__ == "__main__":
    main()