from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
import google.generativeai as genai
import pandas as pd

import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class MyXLSXLoader:
    def __init__(self, xlsx_file):
        self.xlsx_file = xlsx_file

    def extract_data(self):
        excel_data = pd.ExcelFile(self.xlsx_file)
        all_data = {}
        for sheet_name in excel_data.sheet_names:
            df = pd.read_excel(self.xlsx_file, sheet_name=sheet_name)
            all_data[sheet_name] = df.to_dict(orient='records')
        return str(all_data)

    def get_conversation_chain(self):
        prompt_template = """
                You are given Excel data in the form of a dictionary. Use the provided data to answer the question and analyze the information for any hidden patterns, correlations, or trends.
                Be as detailed as possible. If the answer is not in the Excel data, state that "The answer is not available in the Excel data."

                You should consider things like:
                - Repeated values or trends in columns
                - Any correlation between different columns
                - Any outliers or unusual entries

                Excel Data:\n{xlsx_data}\n
                Question:\n{question}\n
                Answer:
        """
        model = GoogleGenerativeAI(model="gemini-pro", temperature=0.1)
        prompt = PromptTemplate(template=prompt_template, input_variables=["xlsx_data", "question"])
        chain = prompt | model
        return chain