import os
import sys
import json
import time
import docx2txt
import streamlit as st
from pages.settings import (
    page_config,
    custom_css,
    delete_folder_contents,
    write_uploaded_file,
)
from pdfminer.high_level import extract_text
from streamlit_extras.switch_page_button import switch_page


# Get the absolute path to the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.abspath(os.path.join(project_root, "src"))
sys.path.insert(0, src_path)

from prompts import summarize_cv, extract_cv_details
from gpt_utils import GPT_UTILS
from json_schema import response_schema

# gpt = GPT_UTILS()

resume_path = f"{project_root}/resumes"


page_config()
custom_css()
if st.sidebar.button("Summarize Text 🗒️", use_container_width=True):
    switch_page("summarization")
if st.sidebar.button("Summarize CV 🗒️", use_container_width=True):
    switch_page("summarize_cv")
if st.sidebar.button("QnA with your data 📒", use_container_width=True):
    switch_page("query_with_data")
if st.sidebar.button("Workout Recommender 🏋🏻", use_container_width=True):
    switch_page("workout_recommendations")
# if st.sidebar.button("Process Resumes ⚙️", use_container_width=True, disabled=True):
#    switch_page("process_resumes")


# Define the header for the page
st.header("Main Page", divider="orange")
st.info(
    """
        Content for Main Page
        """
)

# st.session_state.valid_key = gpt.validate_key()

if not st.session_state.valid_key:
    st.warning("Invalid Open AI API Key. Please re-configure your Open AI API Key.")

st.write(st.session_state.gpt)
