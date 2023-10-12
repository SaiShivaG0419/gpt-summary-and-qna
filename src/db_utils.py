""" A python file to process text or documents into text chunks followed by embeddings to store in vector databases.
    It also provides the utilitie to clear the persisted db.
"""

import os
import time
import json
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain.document_loaders import (
    TextLoader,
    PDFMinerLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
)
from langchain.docstore.document import Document
from langchain.document_loaders import YoutubeLoader


# Get the absolute path to the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# Load the config.json file
with open(f"{project_root}/config/config.json", "r") as config_file:
    config = json.load(config_file)

# Load Config Values
KNOWLDGE_BASE_DIR = config[
    "KNOWLDGE_BASE_DIR"
]  # Load Knowledge base directory name
FAISS_DB_DIR = config["FAISS_DB_DIR"]  # Load Vector database directory name
CHUNK_SIZE = config["CHUNK_SIZE"]  # Loading Text chunk size as integer variable
CHUNK_OVERLAP = config["CHUNK_OVERLAP"]  # Loading Text chunk overlap as integer variable

# Path for the temporary documents
temp_dir_path = f"{project_root}/temp_docs"

knowledge_base_path = f"{project_root}/{KNOWLDGE_BASE_DIR}"
faiss_db_path = f"{project_root}/{FAISS_DB_DIR}"


class VECTOR_DB_UTILS:
    """A class to define various utilities for vector databases."""

    def __init__(self) -> None:
        self.temp_dir_path = temp_dir_path
        self.knowledge_base_path = knowledge_base_path
        self.db_path = faiss_db_path
        self.chunk_size = CHUNK_SIZE
        self.chunk_overlap = CHUNK_OVERLAP

    def create_documents(self, task_type) -> list:
        """A method to extract the document contents from the documents that exist in a folder and returns the list of documents."""

        loader_mapping = {
            ".pdf": PDFMinerLoader,
            ".docx": UnstructuredWordDocumentLoader,
            ".txt": TextLoader,
            ".xlsx": UnstructuredExcelLoader,
        }

        if task_type == "Summarization":
            dir_path = self.temp_dir_path
        elif task_type == "QnA":
            dir_path = self.knowledge_base_path

        # Check if documents folder exist and not empty
        if os.path.exists(dir_path) and os.listdir(dir_path):
            # Define empty documents list
            documents = []

            # Iterate over files and extract the text from documents
            for file_name in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file_name)
                ext = "." + file_path.rsplit(".", 1)[-1]

                if ext in loader_mapping:
                    loader_class = loader_mapping[
                        ext
                    ]  # get the defined loader class for the given file type
                    loader = loader_class(file_path)  # define the loader for the file
                    document_contents = (
                        loader.load()
                    )  # extract the document contents using loader
                    documents.extend(
                        document_contents
                    )  # Append the existing document list
                else:
                    raise ValueError(f"Unsupported file extension: {ext}")

            return documents
        else:
            return None

    def _get_video_info(self, yt_url) -> dict:
        """Get important video information.

        Components are:
            - title
            - description
            - thumbnail url,
            - publish_date
            - channel_author
            - and more.
        """
        try:
            from pytube import YouTube

        except ImportError:
            raise ImportError(
                "Could not import pytube python package. "
                "Please it install it with `pip install pytube`."
            )
        yt = YouTube(yt_url)
        video_info = {
            "title": yt.title,
            "description": yt.description,
            "view_count": str(yt.views),
            "thumbnail_url": yt.thumbnail_url,
            "publish_date": yt.publish_date.strftime("%d/%m/%Y"),
            "length": f"{yt.length /60:.2f} Minutes",
            "author": yt.author,
        }
        return video_info

    def youtube_transcript(self, yt_url):
        """A method to extract transcriptions from Youtube video and create"""
        try:
            loader = YoutubeLoader.from_youtube_url(
                youtube_url=yt_url, add_video_info=True
            )
            yt_transcript = loader.load()
            # return [Document(page_content=yt_transcript, metadata={"source": yt_url})]
            return yt_transcript
        except Exception as e:
            print(f"Error while loading transcripts from youtube video: {e}")
            return None

    def docs_generator(self, task_type, input_type, page_content="", source_url=""):
        """A function to define the logic to generate documents based on input type."""

        if input_type == "documents":
            documents = self.create_documents(task_type)
        elif input_type == "web_url":
            documents = [
                Document(page_content=page_content, metadata={"source": source_url})
            ]
        elif input_type == "yt_url":
            documents = self.youtube_transcript(yt_url=source_url)
        
        return documents
    
    def split_documents(self, task_type, documents, chunk_size=1000, chunk_overlap=0):
        """A function to define the logic to split the documents by either define character chunk size or token size."""

        # Define the text splitter configurations
        if task_type == "Summarization":
            text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        elif task_type == "QnA":
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )
        
        if not documents:
            print("No new document to process")
            return None
        else:
            text_chunks = text_splitter.split_documents(documents)

        return text_chunks

    def run_db_build(
        self,
        input_type,
        embeddings,
        page_content="",
        source_url="",
        db_persist: bool = True,
        **kwargs,
    ):
        """A method to build the vector db and store in the defined database path."""
        try:
            start_time = time.time()
            os.makedirs(self.db_path, exist_ok=True)

            # Get extracted documents content
            documents = self.docs_generator("QnA", input_type, page_content, source_url)

            # Get the text chunks
            if documents is not None:
                processed_documents = self.split_documents(task_type="QnA", documents=documents)
            else:
                print("No document content is provided.")

            # Build vector db
            db = FAISS.from_documents(
                documents=processed_documents, embedding=embeddings
            )

            if db_persist:
                db.save_local(self.db_path)
                # Implement logic to save the db to local

            end_time = time.time()

            return db, end_time - start_time

        except Exception as e:
            error_msg = f"An error occurred while reading files: {e}"
            print(error_msg)
            return None, 0.00

    def load_local_db(self, embeddings):
        """A simple method to load locally saved vector database."""
        if os.path.exists(self.db_path) and os.path.isfile(
            os.path.join(self.db_path, "index.faiss")
        ):
            return FAISS.load_local(self.db_path, embeddings)
        else:
            return None
