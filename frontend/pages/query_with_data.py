""" A Streamlit page that takes the documents and provide an interface to query with the data available in the document.
"""
import os
import sys
import time
import streamlit as st
from pages.settings import (
    page_config,
    custom_css,
    switch_main,
    delete_folder_contents,
    write_uploaded_files,
    count_files_in_directory,
)
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

# Load Environment Variables
KNOWLDGE_BASE_DIR = os.environ[
    "KNOWLDGE_BASE_DIR"
]  # Load Knowledge base directory name
FAISS_DB_DIR = os.environ["FAISS_DB_DIR"]  # Load Vector database directory name

# Get the absolute path to the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
src_path = os.path.abspath(os.path.join(project_root, "src"))
sys.path.insert(0, src_path)

# Loading prompt templates and GPT Utilities from src
from prompts import prompt_doc_qa
from db_utils import VECTOR_DB_UTILS
from url_utils import *

# Initialize Vector database
vector_db = VECTOR_DB_UTILS()

# Path for the knowledge base documents
kb_path = f"{project_root}/{KNOWLDGE_BASE_DIR}"
db_path = f"{project_root}/{FAISS_DB_DIR}"


if "db_exist" not in st.session_state:
    st.session_state.db_exist = False


def input_documents():
    """A streamlit function to provide upload interface for documents and extract information from it."""

    with st.form("Input_Documents"):
        uploaded_files = st.file_uploader(
            label="Upload documents",
            type=["pdf", "docx", "xlsx", "txt"],
            accept_multiple_files=True,
            disabled=not st.session_state.valid_key,
        )
        submit_button = st.form_submit_button(
            label="Upload Documents", disabled=not st.session_state.valid_key
        )

        if submit_button:
            # Upload all the documents to a temporary directory
            upload_state = write_uploaded_files(
                uploaded_files=uploaded_files, folder_path=kb_path
            )
            if not upload_state:
                st.error("Error while uploading files. Please check input files.")


def input_url():
    """A streamlit function to extract text content from web url."""

    with st.form("Input_WebURL"):
        input_url = st.text_input(
            label="Paste a Web URL",
            value="""https://en.wikipedia.org/wiki/Eiffel_Tower""",
        )
        submit_url = st.form_submit_button(
            label="Extract Web Page Content", disabled=not st.session_state.valid_key
        )

        if submit_url:
            # Extract web page content from the given URL
            if validate_input_url(input_url):
                extracted_text = extract_text_url(input_url)
                if len(extracted_text) == 0:
                    st.error(
                        "Unable to extract text content from this URL. Please try other URL."
                    )
                else:
                    # Convert into chunks and build db
                    db, db_build_time = vector_db.run_db_build(
                        input_type="web_url",
                        embeddings=st.session_state.gpt.embeddings,
                        page_content=extracted_text,
                        source_url=input_url,
                        db_persist=True,
                    )
                    if db is not None:
                        st.info(
                            f"Database build completed in {db_build_time:.4f} seconds"
                        )
                        st.session_state.db_exist = True
                        return st.session_state.db_exist
                    else:
                        st.session_state.db_exist = False
                        return st.session_state.db_exist

            else:
                st.error("Invalid URL. Please correct and submit again.")
                st.session_state.db_exist = False
                return st.session_state.db_exist


def process_documents(persist_db: bool = True):
    """A streamlit function to convert the uploaded document files into chunks and store in vector db."""
    try:
        db, db_build_time = vector_db.run_db_build(
            input_type="documents",
            embeddings=st.session_state.gpt.embeddings,
            db_persist=persist_db,
        )
        if db is not None:
            st.info(f"Database build completed in {db_build_time:.4f} seconds")
            st.session_state.db_exist = True
            return st.session_state.db_exist
        else:
            st.session_state.db_exist = False
            return st.session_state.db_exist

    except Exception as e:
        error_msg = f"An error occurred while reading files: {e}"
        st.error(error_msg)
        st.session_state.db_exist = False
        return st.session_state.db_exist


def delete_vector_database():
    """A streamlit function show a button and metric to drop a vector database."""
    try:
        drop_database = st.button(
            label="Reset Vector Database", use_container_width=True
        )
        if drop_database:
            delete_folder_contents(db_path)

        st.metric(
            label="Files in Vector database", value=count_files_in_directory(db_path)
        )
    except Exception as e:
        st.error(f"Error deleting vector database: {e}")


def query_with_data():
    """A streamlit function to load the page to upload documents and query with the data. You can input data in two ways:
    1. A text document such as PDF or DOCX.
    2. A Web Page or Blog URL.
    3. A YouTube URL.
    """

    # Load the page config and custom css from settings
    page_config()
    custom_css()
    switch_main()

    # Define the header for the page
    st.header("QnA with your data", divider="orange")
    # st.divider()
    st.info(
        """
            Upload your text data, paste a web page url or paste a YouTube URL to ask queries or retrieve needed information from the uploaded information :\n
            1. Query with text documents such as PDF, DOCX, XLSX, or TXT.
            2. Query with content from web page or blog posts.
            3. Query with content from a YouTube Video.
            """
    )

    if not st.session_state.valid_key:
        st.warning("Invalid Open AI API Key. Please re-configure your Open AI API Key.")

    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        input_option = st.radio(
            label="Select an input option",
            options=["Upload document(s)", "Paste an URL", "Paste a YouTube URL"],
        )
        if input_option == "Upload document(s)":
            input_documents()
            st.sidebar.info(
                """
                            **Steps to Manage Knowledge Base:**\n
                            1. Browse to select files and click "Upload Documents" to upload selected files to knowledge base.
                            2. In the right side, **KB_Snapshot** tab displays file count and you can reset directory by clicking **Reset Local Directory** button.
                            3. In the **Manage_DB** tab, click **Build Vector Database** to build the vector database. Upon successful build, File count should be 2.
                            4. Optionally, you can reset the vector database by clicking **Reset Vector Database** button.
                            5. Once knowledge base built, you can proceed to ask the related questions from documents.
                            """
            )

            with col2:
                with st.expander("", expanded=True):
                    tab1, tab2 = st.tabs(["KB_Snapshot", "Manage_DB"])
                    with tab1:
                        if st.button(
                            "Reset Local Directory 🚮", use_container_width=True
                        ):
                            delete_folder_contents(kb_path)
                        st.metric(
                            label="Files in Local Directory",
                            value=count_files_in_directory(kb_path),
                        )
                    with tab2:
                        digest_button = st.button(
                            label="Build Vector Database",
                            disabled=not st.session_state.valid_key,
                            use_container_width=True,
                        )
                        if digest_button:
                            db_state = process_documents()

                        # Drop vector database
                        delete_vector_database()

        elif input_option == "Paste an URL":
            input_url()
            st.sidebar.info(
                """
                            **Steps to Manage Knowledge Base:**\n
                            1. Paste a Web URL or blog page URL and click on **Extract Web Page Content** to extract content and build the vector database. Upon successful build, file count should be 2.
                            2. Optionally, you can reset the vector database by clicking **Reset Vector Database** button.
                            3. Once knowledge base built, you can proceed to ask the related questions from documents.
                            """
            )

            with col2:
                with st.expander("", expanded=True):
                    # Drop vector database
                    delete_vector_database()

        elif input_option == "Paste a YouTube URL":
            with st.form("Input_WebURL"):
                yt_url = st.text_input(
                    label="Paste an YouTube URL",
                    value="""https://youtu.be/S951cdansBI""",
                )
                submit_url = st.form_submit_button(
                    label="Extract YouTube Video Transcript",
                    disabled=not st.session_state.valid_key,
                )

                if submit_url:
                    # Validate the YouTube Video URL
                    if validate_youtube_url(yt_url):
                        db, db_build_time = vector_db.run_db_build(
                            input_type="yt_url",
                            embeddings=st.session_state.gpt.embeddings,
                            source_url=yt_url,
                            db_persist=True,
                        )
                        # video_info = vector_db._get_video_info(yt_url)
                        if db is not None:
                            st.info(
                                f"Database build completed in {db_build_time:.4f} seconds"
                            )
                    else:
                        st.error("Invalid URL. Please correct and submit again.")
            st.sidebar.info(
                """
                            **Steps to Manage Knowledge Base:**\n
                            1. Paste an YouTube Video URL and click on **Extract YouTube Transcript** to extract content and build the vector database. Upon successful build, file count should be 2.
                            2. Optionally, you can reset the vector database by clicking **Reset Vector Database** button in **Manage_DB** tab.
                            3. **Video Details** tab provides video info and **Watch Video** provides the embedded YouTube video to watch.
                            4. Once knowledge base built, you can proceed to ask the related questions from documents.
                            """
            )

            with col2:
                with st.expander("", expanded=True):
                    tab1, tab2, tab3 = st.tabs(
                        ["Manage_DB", "Video Details", "Watch Video"]
                    )
                    with tab1:
                        # Drop vector database
                        delete_vector_database()
                    if validate_youtube_url(yt_url):
                        with tab2:
                            video_info = vector_db._get_video_info(yt_url)
                            st.dataframe(video_info, use_container_width=True)
                        with tab3:
                            st.video(yt_url)
                    else:
                        tab2.error("Invalid URL. Please correct and submit again.")
                        tab3.error("Invalid URL. Please correct and submit again.")

    st.divider()
    response = None

    with st.form("QnA_Data"):
        input_query = st.text_input(
            label="Please enter the query that can be answered from available database",
            placeholder="Enter your query",
        )
        return_source_docs = st.toggle(label="Return Source documents info", value=True)
        submit_query = st.form_submit_button(
            label="Submit Query", disabled=not st.session_state.valid_key
        )

    if submit_query:
        start_time = time.time()
        local_db = vector_db.load_local_db(embeddings=st.session_state.gpt.embeddings)
        if local_db is not None:
            with st.spinner("Retrieving response ..."):
                response = st.session_state.gpt.retrieval_qa(
                    query=input_query,
                    prompt=prompt_doc_qa(),
                    db=local_db,
                    return_source_documents=return_source_docs,
                )
        else:
            st.error("Database does not exist. Please build the database first.")
        end_time = time.time()
    if response is not None:
        response_completion = response["result"]
        response_source_docs = []
        if return_source_docs:
            source_docs = response["source_documents"]
            for document in source_docs:
                response_source_docs.append(
                    {
                        "source": document.metadata["source"],
                        "content": document.page_content,
                    }
                )

        with st.expander("", expanded=True):
            st.markdown(response_completion)
        if return_source_docs:
            st.markdown(
                f"<p style='font-size: smaller; color: green;'>Source documents: {response_source_docs}</p>",
                unsafe_allow_html=True,
            )
        st.markdown(
            f"<p style='font-size: smaller; color: green;'>Reponse time: {(end_time - start_time):.4f} seconds</p>",
            unsafe_allow_html=True,
        )


query_with_data()
