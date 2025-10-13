import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

embedding_function = HuggingFaceEmbeddings(model_name="mixedbread-ai/mxbai-embed-large-v1")

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
persist_dir = os.path.join(project_root, "data", "chroma_db")
vectorstore=Chroma(persist_directory=persist_dir,embedding_function=embedding_function)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300, length_function=len)

def index_document_to_chroma(file_path:str,file_id:int):
    try:
        if file_path.endswith('.pdf'):
            logging.error('Logging pdf file')
            loader=PyPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            logging.error('Logging docx file')
            loader=Docx2txtLoader(file_path)
        elif file_path.endswith('.html'):
            logging.error('Logging html file')
            loader=UnstructuredHTMLLoader(file_path)
        else:
            logging.error(f"Unsupported file type: {file_path}")
            raise ValueError(f"Unsupported file type: {file_path}")

        documents=loader.load()
        split_docs=text_splitter.split_documents(documents)

        for split in split_docs:
            split.metadata['file_id']=file_id
            logging.debug(f"Added metadata file_id={file_id} to chunk: {split.page_content[:50]}...")
        
        vectorstore.add_documents(split_docs)
        logging.info(f"Successfully indexed {len(split_docs)} documents to Chroma")
        logging.info(f"Chroma collection count after indexing: {vectorstore._collection.count()}")
        return True
    except Exception as e:
        logging.error(f"Error indexing document {file_path}: {str(e)}")
        return False
    
def delete_doc_from_chroma(file_id:int):
    try:
        docs=vectorstore.get(where={'file_id':file_id})
        logging.info(f"Found {len(docs['ids'])} document chunks for file_id {file_id}")
        vectorstore._collection.delete(where={'file_id':file_id})
        logging.info(f"Deleted all instances with file_id {file_id}")
        logging.info(f"Chroma collection count after deletion: {vectorstore._collection.count()}")
        return True
    except Exception as e:
        logging.error(f"Error deleting document with file_id {file_id} from Chroma: {str(e)}")
        return False