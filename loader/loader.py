import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class BaseLoader:
    def __init__(self):
        pass
    def get_text_chunks(self, text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)
        return chunks
    def get_vector_store(self, text_chunks):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")
        return vector_store
    def get_conversational_chain(self):
        prompt_template = """
        Answer the question as detailed as possible from the provided context. Make sure to provide all the details. 
        If the answer is not in the provided context, just say, "answer is not available in the context." Don't provide a wrong answer.\n\n
        Context:\n{context}\n
        Question:\n{question}\n
        Answer:
        ### NO PREAMBLE
        """
        model = ChatGoogleGenerativeAI(model="gemini-pro", temparature=0.1)
        prompt = PromptTemplate(template=prompt_template, input_variables = ["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt = prompt)
        return chain
    def handle_user_input(self, user_question):
        embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
        vector_store = FAISS.load_local("faiss_index", embeddings)
        docs = vector_store.similarity_search(user_question)

        chain = self.get_conversational_chain()
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        return response["output_text"]