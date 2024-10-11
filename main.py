import os
from dotenv import load_dotenv
from loader.pdf import PDFLoader

load_dotenv()

class Chain:
    def __init__(self):
        self.pdf_loader = None
        self.vector_store = None
    def update_knowledge_base(self, pdf_file_path):
        self.pdf_loader = PDFLoader(pdf_file_path)
        extracted_text = self.pdf_loader.extract_text()
        text_chunks = self.pdf_loader.get_text_chunks(extracted_text)
        self.vector_store = self.pdf_loader.get_vector_store(text_chunks)
        print("Knowledge base updated successfully")
    def handle_query(self, question):
        if not self.vector_store:
            return "No knowledge base is set. Please uploade a file to set the knowledge base."
        docs = self.vector_store.similarity_search(question)
        if not docs:
            return "No relevant information founf in the knowledge base."
        response = self.pdf_loader.get_conversational_chain()(
            {"input_documents": docs, "question": question}, return_only_outputs=True
        )
        return response["output_text"]

chain_instance = Chain()

def handle_query(question):
    return chain_instance.handle_query(question)

def update_knowledge_base(pdf_file_path):
    chain_instance.update_knowledge_base(pdf_file_path)
    return "Knowledge base updated successfully. You can now ask questions."

# if __name__ == "__main__":
#     pdf_file_path = input("Enter the path to the PDF file: ")
#     if os.path.exists(pdf_file_path):
#         update_knowledge_base(pdf_file_path)
#         print("Knowledge base updated successfully. You can now ask questioins.")
#
#         while True:
#             question = input("Enter your question (or 'exit' to quit): ")
#             if question.lower() == "exit":
#                 break
#             response = handle_query(question)
#             print("Response from LLM: ", response)
#     else:
#         print("The specified file does not exist")