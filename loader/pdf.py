try:
    from loader.doc_processor import DocProcessor
except ImportError:
    from doc_processor import DocProcessor
from langchain_community.document_loaders import PyPDFLoader
import os

class PDFLoader(DocProcessor):
    def __init__(self, pdf_file):
        super().__init__()  # Initialize the base class
        self.pdf_file = pdf_file

    def extract_text(self):
        """Extracts text from the provided PDF file."""
        loader = PyPDFLoader(self.pdf_file)
        pages = []
        for page in loader.load():
            pages.append(page)
        content = "".join([page.page_content for page in pages])
        return content

    def process(self):
        """Extracts text, chunks it, and stores vectors in the FAISS index."""
        text = self.extract_text()
        text_chunks = self.get_text_chunks(text)
        self.get_vector_store(text_chunks)
