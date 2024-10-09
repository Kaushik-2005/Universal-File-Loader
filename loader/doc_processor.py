import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class DocProcessor:
    def __init__(self):
        pass

    def get_text_chunks(self, text):
        """Splits the input text into manageable chunks."""
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)
        return chunks

    def get_vector_store(self, text_chunks):
        """Generates vector embeddings for the text chunks and stores them in a FAISS index."""
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")
        return vector_store

    def get_conversational_chain(self):
        """Creates a question-answer chain with a custom prompt using Google Generative AI."""
        prompt_template = """
        Answer the question as detailed as possible from the provided context. Make sure to provide all the details.
        If the answer is not in the provided context, just say, "The answer is not available in the context." Don't provide a wrong answer.\n\n
        Context:\n{context}\n
        Question:\n{question}\n
        Answer:
        """
        model = GoogleGenerativeAI(model="gemini-pro", temperature=0.3)  # Use Google Generative AI
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
        return chain

    def handle_user_input(self, user_question):
        """Handles user input by searching the vector store and generating a response."""
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.load_local("faiss_index", embeddings)
        docs = vector_store.similarity_search(user_question)

        if not docs:
            return "No relevant documents found in the knowledge base."

        chain = self.get_conversational_chain()
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        return response["output_text"]
