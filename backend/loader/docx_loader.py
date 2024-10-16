from docx import Document
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
import google.generativeai as genai

import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class MyDOCXLoader:
    def __init__(self, docx_file):
        self.docx_file = docx_file

    def extract_data(self):
        doc = Document(self.docx_file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)

    def get_conversational_chain(self):
        prompt_template = """
        You are given the content of a Word document. Use the provided data to answer the question and analyze the information.
        Be as detailed as possible. If the answer is not in the document content, state that "The answer is not available in the document."

        Document Content:\n{docx_data}\n
        Question:\n{question}\n
        Answer:
        """
        model = GoogleGenerativeAI(model="gemini-pro", temperature=0.2)
        prompt = PromptTemplate(template=prompt_template, input_variables=["docx_data", "question"])
        chain = prompt | model
        return chain