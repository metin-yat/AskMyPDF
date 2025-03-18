# ChatPDF: Your Document Chatbot

This project lets you chat with your PDF documents. It uses a combination of powerful technologies to make this happen:

**What it does:**

* **Upload PDFs:** You upload your documents.
* **Choose a Model:** Select a language model (powered by Ollama).
* **Ask Questions:** Chat with your documents and get answers.

**Technologies:**

* **FastAPI (Backend):** Handles the API, file uploads, and processing.
* **Streamlit (Frontend):** Provides a user-friendly web interface.
* **LangChain:** Helps with document processing and language model interactions.
* **Ollama:** Runs the language models.
* **Python:** The programming language used to build the application.
* **Docker-compose:** For containerization and easy deployment.

**How to run:**

I am currently making changes to the Ollama container build process. Additionally, the container does not send the entire message history to the model by default. Since this setup is still under development and not yet ready for deployment, here’s how you can execute it easily.

Keep in mind that the default model installation may take some time, so it is recommended to track the API logs during the process.

1.  **Clone the repository:** `git clone https://github.com/metin-yat/AskMyPDF.git`
2.  **Navigate to the project directory:** `cd AskMyPDF`
3.  **Run Docker Compose:** `docker-compose up --build`
4.  **Open in browser:** Go to `http://localhost:8501`.

**Purpose:**

This application simplifies the process of extracting information from your PDFs. Instead of reading through long documents, you can simply ask questions and get direct answers.