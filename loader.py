import os.path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader

class FileLoader:
    def __init__(self):
        pass

    def load_file(self, file):
        file_extension = os.path.splitext(file.name)[1].lower()

        if file_extension == ".pdf":
            return self.load_pdf(file)
        elif file_extension == '.csv':
            return self.load_csv(file)
        else:
            return "Unsupported File Type"

    async def load_pdf(self, file):
        loader = PyPDFLoader(file)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
        content = ""
        for i in pages:
            content += i.page_content
        return content

    def load_csv(self, file):
        loader = CSVLoader(file)
        data = loader.load()
        content = []
        for i in data:
            content.append(i.page_content)
        return content