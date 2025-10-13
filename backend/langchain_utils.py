from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing import List
from langchain_core.documents import Document
import os
from backend.chroma_utils import vectorstore
from dotenv import load_dotenv


load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

retriever = vectorstore.as_retriever(search_kwargs={"k": int(os.getenv("RETRIEVER_K"))})

output_parser = StrOutputParser()

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Use the following context to answer the user's question in detail."),
    ("system", "Context: {context}"),  
    ("human", "{input}")              
])


def get_rag_chain_no_history(model='gemini-2.5-flash'):
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=GOOGLE_API_KEY,
        temperature=float(os.getenv('LLM_TEMPERATURE'))
    )

    # Chain that stuffs documents + user query into LLM
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # Retrieval chain orchestrates: query -> retriever -> QA chain
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    return rag_chain