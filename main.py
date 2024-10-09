import os
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from loader.pdf import PDFLoader

load_dotenv()

class Chain:
    def __init__(self):
        # Initialize the LLM with the given model
        self.llm = GoogleGenerativeAI(model="gemini-pro", temperature=0.3)  # Use Google Generative AI
        self.knowledge_base = ""  # Initialize an empty knowledge base

    def set_knowledge_base(self, content):
        # Set the knowledge base content and create a prompt
        self.knowledge_base = content
        prompt = PromptTemplate.from_template(
            """
            ### PROVIDED CONTENT:
            {content}
            ### INSTRUCTION:
            The above content is the sole knowledge available to the LLM. 
            Your job is to answer any questions using only the provided content. If a question is asked that cannot be answered with the given content, respond with: "The requested information is not available in the provided content."
            Only answer based on the provided content and nothing else.
            ### RESPONSE FORMAT (NO PREAMBLE):
            """
        )
        # Create the chain by linking the prompt with the LLM
        self.chain = prompt | self.llm

    def handle_query(self, question):
        # Check if the knowledge base is available before processing the query
        if not self.knowledge_base:
            return "No knowledge base is set. Please upload a file to set the knowledge base."

        # Generate the response using the provided content and the question
        response = self.chain.invoke(input={"content": self.knowledge_base, "question": question})
        return response


# Initialize the Chain object
chain_instance = Chain()

def handle_query(question):
    return chain_instance.handle_query(question)

def update_knowledge_base(text):
    # Function to update the knowledge base with new text content
    chain_instance.set_knowledge_base(text)
    return "Knowledge base updated successfully"

# Test the Q&A functionality in the terminal
if __name__ == "__main__":
    pdf_file_path = input("Enter the path to the PDF file: ")

    if os.path.exists(pdf_file_path):
        # Create an instance of PDFLoader and extract text
        pdf_loader = PDFLoader(pdf_file_path)
        extracted_text = pdf_loader.extract_text()

        # Update the knowledge base with the extracted text
        update_knowledge_base(extracted_text)

        print("Knowledge base updated successfully. You can now ask questions.")

        while True:
            question = input("Enter your question (or 'exit' to quit): ")
            if question.lower() == 'exit':
                break
            response = handle_query(question)
            print("Response from LLM:", response)
    else:
        print("The specified file does not exist.")
