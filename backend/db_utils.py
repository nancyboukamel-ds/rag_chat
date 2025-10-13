from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
from dotenv import load_dotenv
from langchain.schema import HumanMessage,AIMessage
import os
import logging
from bson.objectid import ObjectId

load_dotenv()
DB_URI = os.getenv("DB_URI")
DB_NAME = os.getenv("DB_NAME")


def get_db_connection():
    try:
        client=MongoClient(DB_URI)
        client.admin.command('ping')
        return client[DB_NAME]
    except ConnectionFailure as e:
        logging.error(F"Failed to connect to MOngodb {str(e)}")
        raise

def initialize_database():
    db=get_db_connection()
    ## index for faster lookup by session_id
    db.application_logs.create_index('session_id')
    ## Ensure document store indexes
    ## Ensure file names are unique
    db.document_store.create_index('filename',unique=True)
    logging.info('Indexes created for document store collection')
    logging.info('Database initialized complete')

def insert_application_logs(session_id,user_query,gpt_response,model):
    db=get_db_connection()
    db.application_logs.insert_one({
        'session_id':session_id,
        'user_query':user_query,
        'gpt_response':gpt_response,
        'model':model,
        'created_at':datetime.now()
    })
    logging.info('Log inserted successfully')

def get_chat_history(session_id):
    ## retrieves chat history for a session from mongodb
    db=get_db_connection()
    ## sort by time stamps ASC
    logs=db.application_logs.find({'session_id':session_id}).sort('created_at',1)
    messages=[]
    for log in logs:
        messages.append(HumanMessage(content=log['user_query']))
        messages.append(AIMessage(content=log['gpt_response']))
    return messages 
    
def insert_document_record(filename):
    ## insert a document record into the document store collection
    db=get_db_connection()
    document={
        'filename':filename,
        'upload_timestamp':datetime.now()
    }
    result=db.document_store.insert_one(document)
    ## return the inserted document's ObjectId as a string
    return str(result.inserted_id)

def delete_document_record(file_id):
    ## delete a document record from the document store collection
    db=get_db_connection()
    try:
        obj_id=ObjectId(file_id)
    except Exception as e:
        logging.error(f"Invalid file_id: {file_id}, error: {str(e)}")
        return False  # Return False if conversion fails (e.g., invalid ObjectId string)
    
    result=db.document_store.delete_one({'_id':obj_id})
    logging.info(f"Delete result for file_id {file_id}: deleted_count={result.deleted_count}")
    return result.deleted_count > 0  # Return True only if a document was actually deleted
    
def get_all_documents():
    db=get_db_connection()
    documents=db.document_store.find().sort('uploaded_timestamp',-1)
    return [{"id": str(doc["_id"]), "filename": doc["filename"], "upload_timestamp": doc["upload_timestamp"]}
            for doc in documents]