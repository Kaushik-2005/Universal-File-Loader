import os
from dotenv import load_dotenv

from handle_file import PDFQueryAssistant, DOCXQueryAssistant, CSVQueryAssistant

load_dotenv()


class DocumentQueryChain:
    def __init__(self):
        self.pdf_assistant = None
        self.csv_assistant = None
        self.docx_assistant = None

    def update_knowledge_base_pdf(self, pdf_file_path):
        """
        Initialize and process PDF for querying
        """
        try:
            self.pdf_assistant = PDFQueryAssistant(pdf_file_path)
            self.pdf_assistant.process_pdf()
            print("PDF knowledge base updated successfully")
        except Exception as e:
            print(f"Error updating PDF knowledge base: {str(e)}")
            raise

    def update_knowledge_base_csv(self, csv_file_path):
        """
        Initialize and process CSV for querying
        """
        try:
            self.csv_assistant = CSVQueryAssistant(csv_file_path)
            self.csv_assistant.process_csv()
            print("CSV knowledge base updated successfully")
        except Exception as e:
            print(f"Error updating CSV knowledge base: {str(e)}")
            raise

    def update_knowledge_base_docx(self, docx_file_path):
        """
        Initialize and process DOCX for querying
        """
        try:
            self.docx_assistant = DOCXQueryAssistant(docx_file_path)
            self.docx_assistant.process_docx()
            print("DOCX knowledge base updated successfully")
        except Exception as e:
            print(f"Error updating DOCX knowledge base: {str(e)}")
            raise

    def handle_query(self, question, file_type):
        """
        Process query based on file type
        """
        try:
            if file_type == 'pdf':
                if not self.pdf_assistant:
                    return "No PDF knowledge base loaded. Please upload a PDF file."
                return self.pdf_assistant.get_response(question)

            elif file_type == 'csv':
                if not self.csv_assistant:
                    return "No CSV knowledge base loaded. Please upload a CSV file."
                return self.csv_assistant.get_response(question)

            elif file_type == 'docx':
                if not self.docx_assistant:
                    return "No DOCX knowledge base loaded. Please upload a DOCX file."
                return self.docx_assistant.get_response(question)

            else:
                return "Unsupported file type. Please use 'pdf', 'csv', or 'docx'."
        except Exception as e:
            print(f"Error handling query: {str(e)}")
            return f"An error occurred while processing your query: {str(e)}"


document_query_chain = DocumentQueryChain()


def handle_query(question, file_type):
    return document_query_chain.handle_query(question, file_type)


def update_knowledge_base(file_path, file_type):
    """
    Update knowledge base for a specific file type
    """
    try:
        if file_type == 'pdf':
            document_query_chain.update_knowledge_base_pdf(file_path)
        elif file_type == 'csv':
            document_query_chain.update_knowledge_base_csv(file_path)
        elif file_type == 'docx':
            document_query_chain.update_knowledge_base_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        return "Knowledge base updated successfully. You can now ask questions."
    except Exception as e:
        print(f"Error updating knowledge base: {str(e)}")
        raise


def main():
    """
    Main interaction loop for document query assistant
    """
    file_path = input("Enter the path to the file (PDF, CSV, or DOCX): ")
    file_type = input("Enter the file type (pdf, csv, or docx): ").lower()

    if os.path.exists(file_path):
        try:
            result = update_knowledge_base(file_path, file_type)
            print(result)

            while True:
                question = input("Enter your question (or 'exit' to quit): ")
                if question.lower() == "exit":
                    break
                response = handle_query(question, file_type)
                print("\nResponse from LLM:", response)
                print("\n" + "-" * 50)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    else:
        print("File not found. Please check the file path and try again.")


if __name__ == "__main__":
    main()