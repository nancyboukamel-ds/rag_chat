from fastapi import FastAPI, File, UploadFile, HTTPException
from backend.chroma_utils import index_document_to_chroma
from backend.pydantic_models import QueryInput,QueryResponse
from backend.langchain_utils import get_rag_chain_no_history
import os
import shutil
import logging
import uuid

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Initialize FastAPI app
app = FastAPI()

@app.post('/upload-doc')
def upload_and_index_document(file:UploadFile=File(...)):
    allowed_extensions=['.pdf','.docx','.html']
    file_extensions= os.path.splitext(file.filename)[1].lower()

    if file_extensions not in allowed_extensions:
        ## server recieved the requested but it cant process it because it is considered invalid, malformed 
        raise HTTPException(status_code=400,detail=f"Unsupported file type. Allowed types are: {','.join(allowed_extensions)}")
    
    ## save the file to the data/documents directory
    documents_dir="data/documents"
    if not os.path.exists(documents_dir):
        os.makedirs(documents_dir)

    tmp_file_path=os.path.join(documents_dir, f"temp_{file.filename}")

    try:
        with open(tmp_file_path,'wb') as buffer:
            shutil.copyfileobj(file.file,buffer)

        success = index_document_to_chroma(tmp_file_path)

        if success:
            return {"message": f"File {file.filename} has been successfully uploaded and indexed."}

    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)


@app.post('/chat',response_model=QueryResponse)
def chat(query_input:QueryInput):
    session_id=query_input.session_id  or str(uuid.uuid4())
    logging.info(f"Session ID: {session_id}, User Query: {query_input.question} Model: {query_input.model.value}")

    rag_chain=get_rag_chain_no_history(query_input.model.value)
    answer=rag_chain.invoke({"input": query_input.question})['answer']

    print('Answer is: ',answer)
    query_response=QueryResponse(
        answer=answer,
        session_id=session_id,
        model=query_input.model
    )

    return query_response
