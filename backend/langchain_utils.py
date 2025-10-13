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

contextualize_q_system_prompt = os.getenv("CONTEXTUALIZE_Q_PROMPT", 
    "Given a chat history and the latest user question " 
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

## for retrieval accuracy
contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

## for answer generation
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Use the following context to answer the user's question in detail."),
    ("system", "Context: {context}"),  
    MessagesPlaceholder('chat_history'),
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

def get_rag_chain_history(model='gemini-2.5-flash'):
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=GOOGLE_API_KEY,
        temperature=float(os.getenv('LLM_TEMPERATURE'))
    )

    ## meant to make retrieval aware of previous interactions when fetching relevant document
    history_aware_retriever=create_history_aware_retriever(llm,retriever,contextualize_q_prompt)

    # Chain that stuffs documents + user query into LLM
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # Retrieval chain orchestrates: query -> retriever -> QA chain
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return rag_chain