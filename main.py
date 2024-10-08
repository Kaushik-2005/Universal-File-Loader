import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        # Initialize the LLM with the given model
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-70b-versatile")
        self.knowledge_base = ""  # Initialize an empty knowledge base

    def set_knowledge_base(self, content):
        # Set the knowledge base content and create a prompt
        self.knowledge_base = content
        prompt = PromptTemplate.from_template(
            """
            ### PROVIDED CONTENT:
            {content}
            ### INSTRUCTION:
            The above content is the sole knowledge available to the LLM. 
            Your job is to answer any questions using only the provided content. If a question is asked that cannot be answered with the given content, respond with: "The requested information is not available in the provided content."
            Only answer based on the provided content and nothing else.
            ### RESPONSE FORMAT (NO PREAMBLE):
            """
        )
        # Create the chain by linking the prompt with the LLM
        self.chain = prompt | self.llm

    def handle_query(self, question):
        # Check if the knowledge base is available before processing the query
        if not self.knowledge_base:
            return "No knowledge base is set. Please upload a file to set the knowledge base."

        # Generate the response using the provided content and the question
        response = self.chain.invoke(input={"content": self.knowledge_base, "question": question})
        return response


# Initialize the Chain object
chain_instance = Chain()

def handle_chat(message):
    # Function to process a chat message (question)
    response = chain_instance.handle_query(message)
    return response

def update_knowledge_base(text):
    # Function to update the knowledge base with new text content
    chain_instance.set_knowledge_base(text)
    return "Knowledge base updated successfully"
