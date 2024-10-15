import os
from dotenv import load_dotenv

from loader.pdf_loader import MyPDFLoader
from loader.csv_loader import MyCSVLoader
from loader.xlsx_loader import MyXLSXLoader

load_dotenv()

class Chain:
    def __init__(self):
        self.pdf_loader = None
        self.csv_loader = None
        self.xlsx_loader = None
        self.vector_store = None
        self.csv_data = None
        self.xlsx_data = None

    def update_knowledge_base_pdf(self, pdf_file_path):
        self.pdf_loader = MyPDFLoader(pdf_file_path)
        extracted_text = self.pdf_loader.extract_text()
        text_chunks = self.pdf_loader.get_text_chunks(extracted_text)
        self.vector_store = self.pdf_loader.get_vector_store(text_chunks)
        print("PDF knowledge base updated successfully")

    def update_knowledge_base_csv(self, csv_file_path):
        self.csv_loader = MyCSVLoader(csv_file_path)
        print("CSV data loaded successfully, ready to answer queries")

    def update_knowledge_base_xlsx(self, xlsx_file_path):
        self.xlsx_loader = MyXLSXLoader(xlsx_file_path)
        print("XLSX data loader successfully, ready to answer queries")

    def handle_query(self, question, file_type):
        if file_type == 'csv':
            if self.csv_loader:
                chain = self.csv_loader.get_conversational_chain()
                response = chain.invoke({"csv_data": str(self.csv_data), "question": question})
                return response
            else:
                return "No CSV data loaded. Please upload a CSV file"

        elif file_type == 'xlsx':
            if self.xlsx_loader:
                chain = self.xlsx_loader.get_conversation_chain()
                response = chain.invoke({"xlsx_data": str(self.xlsx_data), "question": question})
                return response
            else:
                return "NO XLSX data loaded. Please uploade a XLSX file"

        elif file_type == 'pdf':
            if not self.vector_store:
                return "No knowledge base is set. Please upload a PDF file."
            docs = self.vector_store.similarity_search(question)
            if not docs:
                return "No relevant information found in the knowledge base."
            
            # Create the context from the retrieved documents
            context = "\n".join([doc.page_content for doc in docs])
            
            chain = self.pdf_loader.get_conversational_chain()
            response = chain.invoke({"context": context, "question": question})
            return response

        else:
            return "Unsupported file type. Please use 'pdf', 'csv', or 'xlsx'."

chain_instance = Chain()

def handle_query(question, file_type):
    return chain_instance.handle_query(question, file_type)

def update_knowledge_base(file_path, file_type):
    if file_type == 'pdf':
        chain_instance.update_knowledge_base_pdf(file_path)
    elif file_type == 'csv':
        chain_instance.update_knowledge_base_csv(file_path)
    elif file_type == 'xlsx':
        chain_instance.update_knowledge_base_xlsx(file_path)
    return "Knowledge base updated successfully. You can now ask questions."

# if __name__ == "__main__":
#     file_path = input("Enter the path to the file (PDF, CSV, or XLSX): ")
#     file_type = input("Enter the file type (pdf, csv, or xlsx): ")
#     if os.path.exists(file_path):
#         update_knowledge_base(file_path, file_type)
#         print("Knowledge base updated successfully. You can now ask questions.")
#
#         while True:
#             question = input("Enter your question (or 'exit' to quit): ")
#             if question.lower() == "exit":
#                 break
#             response = handle_query(question, file_type)
#             print("Response from LLM: ", response)
