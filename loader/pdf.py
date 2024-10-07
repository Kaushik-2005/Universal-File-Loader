from loader import BaseLoader

from langchain_community.document_loaders import PyPDFLoader


class PDFLoader(BaseLoader):
    def __init__(self, pdf_files):
        self.pdf_file = pdf_files

    async def extract_text(self):
        loader = PyPDFLoader(self.pdf_file)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
        content = ""
        for i in pages:
            content += i.page_content
        return content

    def process(self):
        text = self.extract_text()
        text_chunks = self.get_text_chunks(text)
        self.get_vector_store(text_chunks)