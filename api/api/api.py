from fastapi import FastAPI, HTTPException, File, Form, UploadFile
import requests, uvicorn
from utils.utils import Agent
import tempfile
import json, os
from langchain_community.vectorstores import Chroma

from pydantic import BaseModel

# The `QueryInput` class defines a data model with `session_id` and `query` attributes.
# Used in question_triggered.
class QueryInput(BaseModel):
    session_id: str
    query: str

app = FastAPI()

#
def get_chat_session(session_id:str):
    session_path = f"./sessions/{session_id}.json"
    if os.path.exists(session_path):
        with open(session_path, 'r') as file:
            data = json.load(file)
        return data
    else:
        raise HTTPException(
            status_code=404, detail="No session with given id.")

def update_chat_session(session_id:str, data:dict):
    session_path = f"./sessions/{session_id}.json"
    with open(session_path, "w") as session_file:
        json.dump(data, session_file, indent=4)

def get_session_agent(agent_details:dict):
    # Creating the session's Agent.
    session_agent = Agent(
        llm_model=agent_details["agent"]
    )
    for x in agent_details.keys():
        session_agent.x= agent_details[x]

    return session_agent
#

@app.get("/")
async def check_connection() -> dict:
    '''This function is just for checking that Streamlit succesfully connects to the API or not.'''
    return {"response": 200}

@app.get("/create-chat-session/")
async def create_chat_session(session:str="unnamed_session") -> dict:
    '''Creates a new chat session by writing an empty JSON file with the specified
    session name.
    
    Parameters
    ----------
    session : str, optional
        String that represents the name of the chat session being created.
        Default value is "unnamed_session" if not provided.
    
    Returns
    -------
        A dictionary with a key "response" that has a value of 200 if the operation is successful.
        Otherwise, the response will have a value of 100, and details about the exception that occurred.
    '''
    try:
        with open(f"./sessions/{session}.json", "w") as session_file:
            json.dump({}, session_file, indent=4)

        return {"response" : 200}
    except Exception as E:
        return {"response" : 100, "exception":E}

@app.get("/get-agent/")
async def get_chat_agent(model:str = "llama3.2:3b31",
                        session:str="unnamed_session") -> dict:
    '''Retrieves a chat agent based on a specified model and updates the chat session
    with the agent details.
    
    Parameters
    ----------
    model : str, optional
        The model that will be used for the chat agent. In this case, the default value is set to "llama3.2:3b31".
        This model will be used to create an instance of the `Agent`
    session : str, optional
        Identifier for a chat session. It is used to retrieve and update chat session data.
    
    Returns
    -------
        A dictionary with a key "response" that has a value of 200 if the operation is successful.
        Otherwise, the response will have a value of 100, and details about the exception that occurred.
    '''
    try:
        data = get_chat_session(session)
        agent =  Agent(model)
        data["agent_details"] = agent.to_dict()
        update_chat_session(session, data)

        return {"response": 200}
    except Exception as E:
        return {"response" : 100, "exception":E}
    
@app.post("/file-event/")
async def file_upload(
        session: str = Form(...),
        file: UploadFile = File(...),
        ):
    '''Handles file uploads, saves the file, updates chat session
    data, and processes the file using an Agent.
    
    Parameters
    ----------
    session : str
        String that represents the name of the chat session being created.
    file : UploadFile
        `UploadFile`, which represents a file uploaded in a multipart form. In this case, 
        it is used to receive the file that the user uploads through a form. 
        The function reads the contents of the uploaded file and processes it
    
    Returns
    -------
        a JSON response with a key "response" and a value of 200.
    
    '''
    byte_data = await file.read()
    data = get_chat_session(session)

    # Creating the session's Agent.
    agent_details = data["agent_details"]
    session_agent = Agent(
        llm_model=agent_details["agent"]
    )
    for x in agent_details.keys():
        session_agent.x= agent_details[x]

    # generating a path for document
    documents_path = f"./documents/{session}/"
    os.makedirs(documents_path, exist_ok=True)
    doc_saving_path = f"{documents_path}/{file.filename}"

    # updating the session_data
    if "docs_uploaded" in data: data["docs_uploaded"].append(doc_saving_path)
    else: data["docs_uploaded"] = [doc_saving_path]

    # Saving the file
    with open(doc_saving_path, "wb") as f:
        f.write(byte_data)
    update_chat_session(session, data)

    session_agent.clear()

    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(byte_data)
        file_path=tf.name
    session_agent.ingest(file_path)
    os.remove(file_path)

    update_chat_session(session, data)

    return {"response": 200}

@app.post("/text-input")
async def question_triggered(data: QueryInput) -> dict:
    '''The function retrieves the agent details and session agent based 
    on the session data, generates a prompt. Then, gets answer from the model 
    by sending the prompt and documents to the Ollama.
    
    Parameters
    ----------
    data : QueryInput
        `QueryInput`. Contain information related to a chat session, such as
        the session ID and the user's query.
    
    Returns
    -------
        A dictionary with a key "generated_text" that
    contains the full text generated by the model based on the input query.
    
    '''
    session_data = get_chat_session(data.session_id)

    agent_details = session_data["agent_details"]
    session_agent = get_session_agent(agent_details)

    prompt = session_agent.generate_prompt(data.query)
    model = agent_details["agent"]

    response = requests.post(
            "http://model:11434/api/generate",
            json={"model": model, "prompt": prompt}
        )

    full_text = "".join(json.loads(line)["response"] for line in response.text.strip().split("\n"))
    return {"generated_text": full_text}

@app.get("/assistants")
async def list_models() -> dict:
    '''Retrieves a list of models from a Ollama.
    
    Returns
    -------
        A dictionary with a key "models" containing a list of models 
        obtained from downloaded models inside the Ollama container.
    
    '''
    response = requests.get("http://model:11434/api/tags")
    response.raise_for_status()
    return {"models": response.json()["models"]}
