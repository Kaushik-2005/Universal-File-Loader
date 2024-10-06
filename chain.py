import os

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-70b-versatile")

    def set_knowlegde_base(self, content):
        prompt = PromptTemplate.from_template(
            """
            ### PROVIDED CONTENT:
            {content}
            ### INSTRUCTION:
            The above content is the sole knowledge available to the LLM. 
            Your job is to answer any questions using only the provided content. If a question is asked that connot be answered with given content, respond with: "The requested information is not available in the provided conten."
            Only answer based on the provided content and nothing else.
            ### RESPONSE FORMAT (NO PREAMBLE):
            """
        )
        chain = prompt | self.llm
        response = chain.invoke(input ={"content": content})
