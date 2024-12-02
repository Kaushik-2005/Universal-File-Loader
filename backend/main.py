import os
from dotenv import load_dotenv

from loader.pdf_loader import MyPDFLoader
from loader.csv_loader import MyCSVLoader
from loader.xlsx_loader import MyXLSXLoader
from loader.docx_loader import MyDOCXLoader

load_dotenv()

class Chain:
    def __init__(self):
        self.pdf_loader = None
        self.csv_loader = None
        self.xlsx_loader = None
        self.docx_loader = None
        self.vector_store = None
        self.csv_data = None
        self.xlsx_data = None
        self.docx_data = None

    def update_knowledge_base_pdf(self, pdf_file_path):
        try:
            self.pdf_loader = MyPDFLoader(pdf_file_path)
            extracted_text = self.pdf_loader.extract_text()
            text_chunks = self.pdf_loader.get_text_chunks(extracted_text)
            self.vector_store = self.pdf_loader.get_vector_store(text_chunks)
            print("PDF knowledge base updated successfully")
        except Exception as e:
            print(f"Error updating PDF knowledge base: {str(e)}")
            raise

    def update_knowledge_base_csv(self, csv_file_path):
        try:
            self.csv_loader = MyCSVLoader(csv_file_path)
            self.csv_data = self.csv_loader.extract_data()
            print("CSV data loaded successfully, ready to answer queries")
        except Exception as e:
            print(f"Error loading CSV data: {str(e)}")
            raise

    def update_knowledge_base_xlsx(self, xlsx_file_path):
        try:
            self.xlsx_loader = MyXLSXLoader(xlsx_file_path)
            self.xlsx_data = self.xlsx_loader.extract_data()
            print("XLSX data loaded successfully, ready to answer queries")
        except Exception as e:
            print(f"Error loading XLSX data: {str(e)}")
            raise

    def update_knowledge_base_docx(self, docx_file_path):
        try:
            self.docx_loader = MyDOCXLoader(docx_file_path)
            self.docx_data = self.docx_loader.extract_data()
            print("DOCX data loaded successfully, ready to answer queries")
        except Exception as e:
            print(f"Error loading DOCX data: {str(e)}")
            raise

    def handle_query(self, question, file_type):
        try:
            if file_type == 'csv':
                if self.csv_loader and self.csv_data:
                    chain = self.csv_loader.get_conversational_chain()
                    response = chain.invoke({"csv_data": str(self.csv_data), "question": question})
                    return response
                else:
                    return "No CSV data loaded. Please upload a CSV file"

            elif file_type == 'xlsx':
                if self.xlsx_loader and self.xlsx_data:
                    chain = self.xlsx_loader.get_conversation_chain()
                    response = chain.invoke({"xlsx_data": self.xlsx_data, "question": question})
                    return response
                else:
                    return "No XLSX data loaded. Please upload an XLSX file"

            elif file_type == 'pdf':
                if not self.vector_store:
                    return "No knowledge base is set. Please upload a PDF file."
                docs = self.vector_store.similarity_search(question)
                if not docs:
                    return "No relevant information found in the knowledge base."
                context = "\n".join([doc.page_content for doc in docs])
                
                chain = self.pdf_loader.get_conversational_chain()
                response = chain.invoke({"context": context, "question": question})
                return response

            elif file_type == 'docx':
                if self.docx_loader and self.docx_data:
                    chain = self.docx_loader.get_conversational_chain()
                    response = chain.invoke({"docx_data": self.docx_data, "question": question})
                    return response
                else:
                    return "No DOCX data loaded. Please upload a DOCX file"

            else:
                return "Unsupported file type. Please use 'pdf', 'csv', 'xlsx', or 'docx'."
        except Exception as e:
            print(f"Error handling query: {str(e)}")
            return f"An error occurred while processing your query: {str(e)}"

chain_instance = Chain()

def handle_query(question, file_type):
    return chain_instance.handle_query(question, file_type)

def update_knowledge_base(file_path, file_type):
    try:
        if file_type == 'pdf':
            chain_instance.update_knowledge_base_pdf(file_path)
        elif file_type == 'csv':
            chain_instance.update_knowledge_base_csv(file_path)
        elif file_type == 'xlsx':
            chain_instance.update_knowledge_base_xlsx(file_path)
        elif file_type == 'docx':
            chain_instance.update_knowledge_base_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        return "Knowledge base updated successfully. You can now ask questions."
    except Exception as e:
        print(f"Error updating knowledge base: {str(e)}")
        raise

if __name__ == "__main__":
    file_path = input("Enter the path to the file (PDF, CSV, XLSX, or DOCX): ")
    file_type = input("Enter the file type (pdf, csv, xlsx, or docx): ").lower()
    if os.path.exists(file_path):
        try:
            result = update_knowledge_base(file_path, file_type)
            print(result)

            while True:
                question = input("Enter your question (or 'exit' to quit): ")
                if question.lower() == "exit":
                    break
                response = handle_query(question, file_type)
                print("Response from LLM: ", response)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    else:
        print("File not found. Please check the file path and try again.")