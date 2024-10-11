from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_google_genai import GoogleGenerativeAI
import google.generativeai as genai
import os
import csv
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configure Google Generative AI API with the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class MyCSVLoader:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.csv_data = []

    def extract_entries(self):
        """
        Extract the CSV file content and store it as a list of rows.
        """
        with open(self.csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            self.csv_data = [row for row in reader]
        return self.csv_data

    def get_conversational_chain(self):
        """
        Create a conversational chain using Google Generative AI for answering questions
        based on the CSV data and analyzing it for hidden patterns, trends, or outliers.
        """
        # Template to guide the model on how to answer the question using CSV data
        prompt_template = """
            You are given CSV data. Use the provided data to answer the question and analyze the information for any hidden patterns, correlations, or trends. 
            Be as detailed as possible. If the answer is not in the CSV data, state that "The answer is not available in the CSV data."

            You should consider things like:
            - Repeated values or trends in columns
            - Any correlation between different columns
            - Any outliers or unusual entries

            CSV Data:\n{csv_data}\n
            Question:\n{question}\n
            Answer:
        """

        # Initialize the Google Generative AI model (temperature controls creativity)
        model = GoogleGenerativeAI(model="gemini-pro", temperature=0.3)

        # Create a prompt template for the chain
        prompt = PromptTemplate(template=prompt_template, input_variables=["csv_data", "question"])

        # Load the QA chain
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

        return chain

    def handle_user_input(self, user_question):
        """
        Process the user's question by first ensuring the CSV data is loaded,
        and then passing both the question and data to the conversational chain.
        """
        # Extract CSV data if not already done
        if not self.csv_data:
            self.extract_entries()

        # Prepare the conversational chain
        chain = self.get_conversational_chain()

        # Create a response by feeding the CSV data and user question into the model
        response = chain({
            "csv_data": " ".join([str(row) for row in self.csv_data]),  # Convert rows to string
            "question": user_question
        }, return_only_outputs=True)

        return response["output_text"]
