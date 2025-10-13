import streamlit as st
import pandas as pd
import numpy as np
import os
import requests

BACKEND_URL = "http://localhost:8000" 
def upload_file_to_backend(uploaded_files_list):

    st.header(f"🚀 Processing {len(uploaded_files_list)} Documents...")
    all_successful = True

    for i,uploaded_file in enumerate(uploaded_files_list,1):
        st.subheader(f"File {i}/{len(uploaded_files_list)}:{uploaded_file.name}")
    
        st.write(f"Uploading and indexing {uploaded_file.name}... please wait.")
        # Use the file's original name to create a File object for the request
        # 'files' dictionary format: {'field_name_in_fastapi': (filename, file_object, content_type)}
        files = {
            'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }

        try:
            response=requests.post(f"{BACKEND_URL}/upload-doc",files=files)

            if response.status_code==200:
                st.success("✅ **Success!** File uploaded and indexed to ChromaDB.")
                st.json(response.json())
            else:
                error_data = response.json()
                error_detail = error_data.get("detail", "Unknown error occurred.")
                st.error(f"❌ **Upload Failed!** Status: {response.status_code}")
                st.error(f"Reason: {error_detail}")
        except requests.exceptions.ConnectionError:
            st.error(
                "🔴 **Connection Error:** Could not connect to the backend server. "
                f"Please ensure your FastAPI server is running at **{BACKEND_URL}**."
            )
        except Exception as e:
            st.exception(f"An unexpected error occurred: {e}")

    st.markdown("---")
    if all_successful:
        st.balloons()
        st.success("🎉 All documents were processed successfully!")
    else:
        st.warning("⚠️ Finished processing. Check the logs for failed files.")


def chat_with_document(user_message):
    try:
        response=requests.post(f"{BACKEND_URL}/chat",json={'question':user_message})
        if response.status_code==200:
            return response.json().get('answer','')
        else:
            return f"Error {response.status_code}-{response.text}"
    except Exception as e:
        return f"Exception: {e}"

def chat_file_ui():
    st.header("Chat with Documents")
    if "messages" not in st.session_state:
        st.session_state.messages=[]

    for msg in st.session_state.messages:
        if msg['role']=='user':
            st.chat_message('user').write(msg['content'])
        else:
            st.chat_message('assistant').write(msg['content'])
    
    if prompt := st.chat_input('Type your message here...'):
        ## Add user message to chat
        st.session_state.messages.append({'role':'user','content':prompt})
        st.chat_message('user').write(prompt)

        ## Get assistant reply from backend
        with st.spinner('Thinking...'):
            reply=chat_with_document(prompt)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)



def list_all_files_ui():
    st.header("📂 List All Files")
    st.write("This will display all uploaded/indexed files.") 


def main():
    st.set_page_config(page_title='Document App',layout='centered')

    menu=['Upload file','Chat File', 'List All Files']
    choice=st.sidebar.radio('Menu',menu)

    if choice=='Upload file':
        st.title("📄 Document Uploader")
        st.markdown("---")

        uploaded_files_list=st.file_uploader(
            'Choose a Document (.pdf,.docx,.html)',
            type=['pdf','docx','html'],
            accept_multiple_files=True,
            key='file_uploader'
        )

        if uploaded_files_list is not None and len(uploaded_files_list) > 0:
            
            # ⚠️ FIX APPLIED HERE: Report the count instead of accessing attributes
            st.info(f"**{len(uploaded_files_list)}** file(s) ready for upload.")
            
            if st.button("Upload and Index"):
                # Call the function with the LIST of files
                upload_file_to_backend(uploaded_files_list) 
    elif choice=='Chat File':
        chat_file_ui()

    elif choice=='List All Files':
        list_all_files_ui()

if __name__ == "__main__":
    main()