import streamlit as st
from streamlit_chat import message
import requests
from utils.api_client import APIClient
from datetime import datetime, timedelta

st.set_page_config(page_title="ChatPDF")

def store_api_logs(response:dict, event:str):
    """
    Stores the API logs in a list so it can be tracked by developers
    if error occurs.

    Args:
        response (dict): HTTP response object from the API
        event (str): Name of the event
    """

    if response["response"] == 200: 
        st.session_state["api_logs"].append(
            f"{event} event succesfully executed")
    else:
        st.session_state["api_logs"].append(
            "{event} event FAILED due to the error occured."\
            f"Error details: {response['exception']}"
        )

def check_session_data_is_valid_to_pass(session:st.session_state):
    st.error(APIClient.check_api_connection(session))

def create_session():
    body = {
        "session_id":st.session_state["session_id"],
        "session": st.session_state["session"]
    }
    create_chat_session = APIClient.create_chat_session(body)

    store_api_logs(response=create_chat_session,
                             event = "Creating Session")

def get_chat_agent():
    """
    Sends a request to an API to get a chat agent based on selected model
    and session information.
    """
    
    body = {
        "selected_model": st.session_state["selected_model"],
        "session": st.session_state["session"],
        "session_id": st.session_state["session_id"]
    }
    agent_request = APIClient.get_chat_agent(body)

    store_api_logs(response=agent_request,
                             event = "Get Chat Agent")

def upload_file_event():
    """
    Uploads files, processes them, and logs the API response.
    """
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""

    files_to_send = []
    for uploaded_file in st.session_state["file_uploader"]:
        files_to_send.append({
            'filename': uploaded_file.name,
            'pdf_data': uploaded_file.getvalue(),
            'content_type': uploaded_file.type 
        })

    ingest_files_request = APIClient.file_upload({
        "file_uploader" : files_to_send,
        "session" : st.session_state["session"],
        "session_id": st.session_state["session_id"],
        }
    )

    store_api_logs(response=ingest_files_request,
                             event = "Ingest Files")


def text_input_event():
    user_input = st.session_state["user_input"]

    if user_input.strip():
        st.session_state["messages"].append(
            (f"{user_input}", True)
        )

        response = APIClient.text_input({
            "user_input": user_input,
            "session" : st.session_state["session"],
            "session_id": st.session_state["session_id"],
        })

        if response["generated_text"]:
            st.session_state["messages"].append(
                (response["generated_text"] , False)
            )

        store_api_logs(response,
                       event= "Text Input and Generating Answer")

def get_available_model_list():
    response = APIClient.list_models({
        "session" : st.session_state["session"],
    })
    if response:
        return response
    return ["Download A model in your container first"]
##
def display_messages():
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))

def page():
    # Initiating chat session
    if len(st.session_state) == 0:
        st.session_state["session"] = requests.Session()
        st.session_state["messages"] = []
        models = get_available_model_list()
        st.session_state["models"] = models
        st.session_state["file_uploader"] = []

        st.session_state["api_logs"] = []

        # Creating session_id.
        time_adjustment_for_istanbul = timedelta(hours=3)
        now = datetime.now() + time_adjustment_for_istanbul
        st.session_state["session_id"] = f"session_{now.strftime('%d-%m-%Y_%H-%M')}"

        create_session()

    # if file(s) is deleted: refresh message history
    if not st.session_state["file_uploader"]:
        st.session_state["messages"] = []

    st.header("Chat with your documents")

    # Model Selection
    st.session_state["selected_model"] = st.selectbox(
        "Which model would you like to talk with?",
        st.session_state["models"],
        index = None,
        placeholder = "Select a model"
    )

    if st.session_state["selected_model"] is None :
        st.warning("You didn't select a model. API will use. You need to"\
                   " select a model to process further.")

    else: 
        get_chat_agent()

        st.write("Selected model and the agent object for that model is : ", 
             st.session_state["selected_model"])

        # Uploading Documents
        st.file_uploader(
            "Upload a document",
            type=["pdf"],
            key="file_uploader",
            on_change=upload_file_event,
            label_visibility="visible",
            accept_multiple_files=True,
        )
        # Displaying Chat History
        st.markdown("""
                <h2 style='text-align: center; color: #F1F1F1;'>--</h2>
            """, unsafe_allow_html=True)

        # Getting the Question if there is a document
        if len(st.session_state["file_uploader"])>0:
            st.text_input(
                "Ask something",
                key="user_input",
                on_change=text_input_event
            )

        else:
            st.info(
                "You can not acces the chat until uploading folders and selecting a model."
                )

        display_messages()

if __name__ == "__main__":
    page()
