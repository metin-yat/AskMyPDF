import requests 
import io 

class APIClient:
    BASE_URL = "http://api:8000"

    @staticmethod
    def check_api_connection(session_state:dict):
        req_session = session_state["session"].get(
            f"{APIClient.BASE_URL}/")
        return req_session  

    @staticmethod
    def create_chat_session(request:dict):
        session, session_id = request["session"], request["session_id"]
        create_session_request = session.get(
            f"{APIClient.BASE_URL}/create-chat-session/?session={session_id}"
        )

        return create_session_request.json()

    @staticmethod
    def get_chat_agent(request:dict):
        session, selected_model, session_id= (
            request["session"], request["selected_model"], request["session_id"])

        agent_response = session.get(
            f"{APIClient.BASE_URL}/get-agent/?session={session_id}&model={selected_model}"
        )

        return agent_response.json()

    @staticmethod
    def file_upload(request:dict) -> dict:
        session = request["session"]
        file_uploader = request["file_uploader"]
        session_id = request["session_id"]

        try:

            for file in file_uploader:
                file_bytes_io = io.BytesIO(file["pdf_data"])
                session.post(
                    f"{APIClient.BASE_URL}/file-event/",
                    files={"file": (file["filename"],
                                    file_bytes_io,
                                    file["content_type"])
                    }, data = {"session": session_id}
                )
            response_dict = {"response":200}
        except Exception as E:
            response_dict = {
                "response": 100,
                "exception":E
            }

        return response_dict

    @staticmethod
    def text_input(request:dict):
        session = request["session"]

        try:
            response = session.post(
                f"{APIClient.BASE_URL}/text-input",
                json={"session_id": request["session_id"],
                    "query": request["user_input"]}
         )
            response_dict = {
                "response": 200,
                "generated_text": response.json()["generated_text"]
            }
        except Exception as E:
            response_dict = {
                "response": 100,
                "exception": E
            }
        return response_dict

    @staticmethod
    def list_models(request:dict):
        session = request["session"]
        response = session.get(
                        f"{APIClient.BASE_URL}/assistants")
        model_names=[x["model"] for x in response.json()["models"]]

        return model_names
