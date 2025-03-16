from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain.schema.output_parser import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.vectorstores.utils import filter_complex_metadata

class Agent(): 
    vector_store:str = None
    retriever:str = None
    chain:str = None

    def __init__(self, llm_model: str = "llama3.2:3b", **kwargs):
        self.model = llm_model 
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024, chunk_overlap=100
        )

        self.vector_store = None
        self.retriever = None
        self.chain = None

    def ingest(self, pdf_file_path: str):
        docs = PyPDFLoader(file_path=pdf_file_path).load()
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)

        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=FastEmbedEmbeddings(),
            persist_directory="chroma_db",
        )

    def generate_prompt(self, query: str):
        """Generate a prompt where the retrieved documents come first, followed by the question."""
        if not self.vector_store:
            self.vector_store = Chroma(
                persist_directory="chroma_db", embedding_function=FastEmbedEmbeddings()
            )

        self.retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 10, "score_threshold": 0.0},
        )

        relevant_documents = self.retriever.invoke(query)

        chunks = ','.join(str(v) for v in relevant_documents)

        prompt = f"{chunks}:Question: {query}"

        return prompt

    def clear(self):
        self.vector_store = None
        self.retriever = None
        self.chain = None
    
    def to_dict(self):
        json_serializable_agent = {
            "agent":self.model,
            "vector_store":self.vector_store,
            "retriever":self.retriever,
            "chain":self.chain
        }
        return json_serializable_agent
