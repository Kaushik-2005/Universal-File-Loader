import os
from dotenv import load_dotenv
from loader.pdf_loader import MyPDFLoader
from loader.csv_loader import MyCSVLoader

load_dotenv()

class Chain:
    def __init__(self):
        self.pdf_loader = None
        self.csv_loader = None
        self.vector_store = None
        self.csv_data = None

    def update_knowledge_base_pdf(self, pdf_file_path):
        self.pdf_loader = MyPDFLoader(pdf_file_path)
        extracted_text = self.pdf_loader.extract_text()
        text_chunks = self.pdf_loader.get_text_chunks(extracted_text)
        self.vector_store = self.pdf_loader.get_vector_store(text_chunks)
        print("PDF knowledge base updated successfully")

    def update_knowledge_base_csv(self, csv_file_path):
        self.csv_loader = MyCSVLoader(csv_file_path)
        csv_text, csv_data = self.csv_loader.extract_entries()
        self.csv_data = csv_data  # Store the CSV data for later queries
        print("CSV data loaded successfully, ready to answer queries")

    def handle_query(self, question, file_type):
        # For CSV files, directly query the loaded CSV data
        if file_type == 'csv':
            if self.csv_data:
                response = self.csv_loader.handle_user_input(question, csv_data=self.csv_data)
                return response
            else:
                return "No CSV data loaded. Please upload a CSV file."
        # For PDF files, proceed with the knowledge base vector store
        elif file_type == 'pdf':
            if not self.vector_store:
                return "No knowledge base is set. Please upload a PDF file to set the knowledge base."

            docs = self.vector_store.similarity_search(question)
            if not docs:
                return "No relevant information found in the knowledge base."

            response = self.pdf_loader.get_conversational_chain()(
                {"input_documents": docs, "question": question}, return_only_outputs=True
            )
            return response["output_text"]

        else:
            return "Unsupported file type. Please use 'pdf' or 'csv'."

chain_instance = Chain()

def handle_query(question, file_type):
    return chain_instance.handle_query(question, file_type)

def update_knowledge_base(file_path, file_type):
    if file_type == 'pdf':
        chain_instance.update_knowledge_base_pdf(file_path)
    elif file_type == 'csv':
        chain_instance.update_knowledge_base_csv(file_path)
    return "Knowledge base updated successfully. You can now ask questions."

# if __name__ == "__main__":
#     file_path = input("Enter the path to the file (PDF or CSV): ")
#     file_type = input("Enter the file type (pdf or csv): ")
#     if os.path.exists(file_path):
#         update_knowledge_base(file_path, file_type)
#         print("Knowledge base updated successfully. You can now ask questions.")
#
#         while True:
#             question = input("Enter your question (or 'exit' to quit): ")
#             if question.lower() == "exit":
#                 break
#             response = handle_query(question)
#             print("Response from LLM: ", response)
#     else:
#         print("The specified file does not exist")