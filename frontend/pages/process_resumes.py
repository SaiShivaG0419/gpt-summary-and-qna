""" A Streamlit python file to collect all the resumes and store it to assigned storage like amazon s3.
"""
import os
import sys
import streamlit as st
from pages.settings import page_config, custom_css, switch_main, delete_folder_contents, write_uploaded_files, count_files_in_directory


# Get the absolute path to the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
src_path = os.path.abspath(os.path.join(project_root, "src"))
sys.path.insert(0, src_path)

from gpt_utils import GPT_UTILS

gpt = GPT_UTILS()

resumes_path = f"{project_root}/resumes_local"

if "valid_key" not in st.session_state:
    st.session_state.valid_key = False


def process_resumes():
    """ A Streamlit function to allow the system to collect the resumes either pdf or docx files only, and write it to desired storage.
        1. Users can go with storing locally to perform quick analysis and wipe the data when session is reset.
        2. Users can choose to store in Amazon S3 to persist and use it for later analysis.
    """

    # Load the page config and custom css from settings
    page_config()
    custom_css()
    switch_main()

    # Define the header for the page
    st.header("Process CV Data")
    st.divider()
    st.info("""
            Upload the resume data from the frontend and process them as required:\n
            1. Choose to upload to temporary directory for quicker analysis.
            2. Choose to upload to Amazon S3 storage for later analysis and persist the database.
            """)
    
    st.session_state.valid_key = gpt.validate_key()

    if not st.session_state.valid_key:
        st.warning("Invalid Open AI API Key. Please update your key and redeploy the app.")


    col1, col2, col3 = st.columns([0.4, 0.3, 0.3])

    with col1:
        form = st.form("Process_CV")
        uploaded_files = form.file_uploader(label="Upload CV files",
                                   type=["pdf", "docx"],
                                   accept_multiple_files=True,
                                   disabled=not st.session_state.valid_key)
        form.info("""
                1. Choose "Dry Run" mode to store data locally and perform quick analysis.
                2. Choose "Live Run" mode to store data in Amazon S3 buckets and persist to analyse later.
                """)
        form.radio(label="Choose Run type", options=["Dry Run", "Live Run"], key="run_type", horizontal=True)
        submit_button = form.form_submit_button(label="Submit", disabled=not st.session_state.valid_key)

        if submit_button:
            if st.session_state.run_type == "Dry Run":
                write_uploaded_files(uploaded_files=uploaded_files, folder_path=resumes_path)
            elif st.session_state.run_type == "Live Run":
                st.error("Yet to be implemented, Please use Dry Run mode for now.")
    
    if st.button("Reset Local Directory 🚮"):
        delete_folder_contents(resumes_path)
 
    with col2:
        with st.expander('', expanded=True):
            st.metric(label="Files in Local Directory", value=count_files_in_directory(resumes_path))
            st.metric(label="Files in Amazon S3 Directory", value=0)
        sub_col1, sub_col2, sub_col3 = st.columns([0.49, 0.02, 0.49])
        digest_resumes = sub_col1.button("Digest Resumes", use_container_width=True)
        start_analysis = sub_col3.button("Get Insights", use_container_width=True)


    if st.session_state.run_type == "Dry Run":
        st.divider()
        #tab1, tab2 = st.tabs("Digest Resumes")
        digest_resumes = st.button("Digest Resumes")
        start_analysis = st.button("Get Insights")




process_resumes()