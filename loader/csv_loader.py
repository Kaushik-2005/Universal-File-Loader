from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI

import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class MyCSVLoader:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.csv_data = []

    def extract_data(self):
        loader = CSVLoader(self.csv_file)
        data = loader.load()
        for i in data:
            self.csv_data.append(i)

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
        # Use LLMChain directly instead of the deprecated load_qa_chain
        chain = LLMChain(llm=model, prompt=prompt)
        return chain

    def handle_user_input(self, user_question):
        if not self.csv_data:
            self.extract_data()
        chain = self.get_conversational_chain()

        # Ensure the keys in the input match those expected by the prompt template
        response = chain.run({
            "csv_data": str(self.csv_data),
            "question": user_question
        })
        return response

# file_path = input("Enter path of CSV file: ")
# csv_loader = MyCSVLoader(file_path)
# csv_loader.extract_data()
#
# while True:  # Loop to continuously prompt for questions
#     query = input("Enter a question (or type 'exit' to quit): ")
#     if query.lower() == 'exit':
#         break  # Exit the loop if the user types 'exit'
#     answer = csv_loader.handle_user_input(query)
#     print("Answer:", answer)