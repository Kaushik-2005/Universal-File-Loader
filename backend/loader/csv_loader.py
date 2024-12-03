from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
import google.generativeai as genai
import os
import re
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class CSVQueryAssistant:
    def __init__(self, csv_file, allow_external_knowledge=True):
        """
        Initialize CSV query assistant

        :param csv_file: Path to the CSV file
        :param allow_external_knowledge: Whether to allow answers from model's knowledge base
        """
        self.csv_file = csv_file
        self.allow_external_knowledge = allow_external_knowledge
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.model = GoogleGenerativeAI(model="gemini-pro", temperature=0.3)
        self.vector_store = None
        self.data = None

    def process_csv(self):
        """
        Process CSV: load data, convert to text, and create vector store
        """
        df = pd.read_csv(self.csv_file)

        # Convert DataFrame to list of text representations
        text_chunks = []
        for index, row in df.iterrows():
            # Create a text representation of each row
            row_text = " | ".join([f"{col}: {str(val)}" for col, val in row.items()])
            text_chunks.append(row_text)

        # Additional text chunk with column information
        column_info = f"Columns: {', '.join(df.columns)}"
        text_chunks.append(column_info)

        # Create vector store
        self.vector_store = FAISS.from_texts(text_chunks, embedding=self.embeddings)
        self.vector_store.save_local("faiss_index_csv")

        # Store original data for reference
        self.data = df

    def strip_markdown(self, text):
        """
        Remove Markdown formatting from text
        """
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[\*\-]\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n{2,}', '\n', text)
        return text.strip()

    def get_response(self, user_question):
        """
        Generate response to user question
        :param user_question: User's input question
        :return: Model's response
        """
        if self.allow_external_knowledge:
            try:
                # If vector store exists and has content, do similarity search
                if self.vector_store:
                    vector_store = FAISS.load_local("faiss_index_csv", self.embeddings,
                                                    allow_dangerous_deserialization=True)
                    docs = vector_store.similarity_search(user_question)

                    prompt_template = """
                    Use the following context as a primary reference, but you are allowed to provide 
                    additional information from your knowledge base if the context does not fully answer the question.
                    If the context provides partial information, supplement it with your broader knowledge.
                    Context:
                    {context}
                    Question:
                    {question}
                    Answer comprehensively, clearly indicating which information comes from the context 
                    and which comes from your broader knowledge.
                    """

                    context = "\n\n".join([doc.page_content for doc in docs])

                    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
                    chain = prompt | self.model

                    response = chain.invoke({"context": context, "question": user_question})
                else:
                    # If no vector store, use full external knowledge
                    prompt_template = """
                    Answer the following question using your comprehensive knowledge base.
                    Question:
                    {question}
                    Answer comprehensively and thoughtfully.
                    """

                    prompt = PromptTemplate(template=prompt_template, input_variables=["question"])
                    chain = prompt | self.model

                    response = chain.invoke({"question": user_question})

                raw_response = response.text if hasattr(response, 'text') else str(response)
                clean_response = self.strip_markdown(raw_response)
                return clean_response

            except Exception as e:
                return f"An error occurred while generating response: {str(e)}"
        else:
            return "No relevant documents found in the knowledge base and external knowledge is not allowed."


def main():
    csv_path = input("Enter path of your CSV file: ")
    assistant = CSVQueryAssistant(csv_path, allow_external_knowledge=True)
    assistant.process_csv()
    while True:
        query = input("Ask a question or ('exit' for quitting): ")
        if query.lower() == 'exit':
            break
        response = assistant.get_response(query)
        print("\nResponse:", response)
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()