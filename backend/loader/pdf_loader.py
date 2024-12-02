from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class PDFQueryAssistant:
    def __init__(self, pdf_file, allow_external_knowledge=True):
        """
        Initialize PDF query assistant

        :param pdf_file: Path to the PDF file
        :param allow_external_knowledge: Whether to allow answers from model's knowledge base
        """
        self.pdf_file = pdf_file
        self.allow_external_knowledge = allow_external_knowledge
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.model = GoogleGenerativeAI(model="gemini-pro", temperature=0.3)
        self.vector_store = None

    def process_pdf(self):
        """
        Process PDF: extract text, split into chunks, and create vector store
        """
        loader = PyPDFLoader(self.pdf_file)
        pages = loader.load()
        content = "".join([page.page_content for page in pages])
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        text_chunks = text_splitter.split_text(content)
        self.vector_store = FAISS.from_texts(text_chunks, embedding=self.embeddings)
        self.vector_store.save_local("faiss_index")

    def strip_markdown(self, text):
        """
        Remove Markdown formatting from text

        This method handles:
        - Bold (**text**)
        - Italics (*text*)
        - Headers (#, ##, ###)
        - Bullet points
        - Numbered lists
        """
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[\*\-]\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n{2,}', '\n', text)
        text = text.strip()
        return text

    def get_response(self, user_question):
        """
        Generate response to user question

        :param user_question: User's input question
        :return: Model's response
        """
        if self.allow_external_knowledge:
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
        else:
            prompt_template = """
            Answer the question as detailed as possible ONLY from the provided context. 
            If the answer is not in the provided context, say "The answer is not available in the context."
            Context:
            {context}
            Question:
            {question}
            Answer:
            """

        vector_store = FAISS.load_local("faiss_index", self.embeddings, allow_dangerous_deserialization=True)
        docs = vector_store.similarity_search(user_question)
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = prompt | self.model

        context = "\n\n".join([doc.page_content for doc in docs])

        if docs:
            try:
                response = chain.invoke({"context": context, "question": user_question})
                raw_response = response.text if hasattr(response, 'text') else str(response)
                clean_response = self.strip_markdown(raw_response)
                return clean_response
            except Exception as e:
                return f"An error occurred while generating response: {str(e)}"
        else:
            if self.allow_external_knowledge:
                try:
                    response = chain.invoke({"context": "No specific context available.", "question": user_question})
                    raw_response = response.text if hasattr(response, 'text') else str(response)
                    clean_response = self.strip_markdown(raw_response)
                    return clean_response
                except Exception as e:
                    return f"An error occurred while generating response: {str(e)}"
            else:
                return "No relevant documents found in the knowledge base."

def main():
    pdf_path = input("enter path of your file: ")
    assistant = PDFQueryAssistant(pdf_path, allow_external_knowledge=True)
    assistant.process_pdf()
    while True:
        query = input("ask a question or ('exit' for quitting): ")
        if query.lower() == 'exit':
            break
        response = assistant.get_response(query)
        print("\nResponse:", response)
        print("\n" + "-" * 50 + "\n")

if __name__ == "__main__":
    main()