from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI

import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class MyCSVLoader:
    def __init__(self, csv_file):
        self.csv_file = csv_file

    def extract_data(self):
        loader = CSVLoader(self.csv_file)
        data = loader.load()
        return [i.page_content for i in data]

    def get_conversational_chain(self):
        prompt_template = """
                You are given CSV data in the form of a list. Use the provided data to answer the question and analyze the information for any hidden patterns, correlations, or trends. 
                Be as detailed as possible. If the answer is not in the CSV data, state that "The answer is not available in the CSV data."

                You should consider things like:
                - Repeated values or trends in columns
                - Any correlation between different columns
                - Any outliers or unusual entries

                CSV Data:\n{csv_data}\n
                Question:\n{question}\n
                Answer:
            """
        model = GoogleGenerativeAI(model="gemini-pro", temperature=0.3)
        prompt = PromptTemplate(template=prompt_template, input_variables=["csv_data", "question"])
        chain = prompt | model
        return chain