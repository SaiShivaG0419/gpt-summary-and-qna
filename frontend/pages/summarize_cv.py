""" A streamlit page to showcase summarization capabilities for CVs and Resumes.
    Page mainly showcases two capabilities:
        1. Summarize the uploaded CV in text formsat.
        2. JSON format with key information from CV.
"""
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
    switch_main,
)
from pdfminer.high_level import extract_text

# Get the absolute path to the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
src_path = os.path.abspath(os.path.join(project_root, "src"))
sys.path.insert(0, src_path)

from prompts import summarize_cv, extract_cv_details
from json_schema import response_schema


resume_path = f"{project_root}/resumes"


page_config()
custom_css()
switch_main()

# Define the header for the page
st.header("Summarize CV", divider="orange")
st.info(
    """
        Extract and summarize the CV or resume using Open AI's GPT Large Language Model. You can select the output type as below:\n
        1. Summerized text covering key information.
        2. JSON format that can be used to use in downstream applications.
        """
)


if not st.session_state.valid_key:
    st.warning("Invalid Open AI API Key. Please re-configure your Open AI API Key.")


summarized_text = ""
tokens_used = 0
exec_time = 0
json_response = ""

col1, col2 = st.columns([0.3, 0.7])

with col1:
    form = st.form("CV_summary")
    uploaded_file = form.file_uploader(
        label="Upload CV file",
        type=["pdf", "docx"],
        on_change=delete_folder_contents(resume_path),
        disabled=not st.session_state.valid_key,
    )
    output_type = form.radio(
        label="Select Output type",
        options=["Text Summary", "JSON Format"],
        horizontal=True,
    )
    word_limit = form.slider(
        label="Select summary word limit",
        min_value=200,
        max_value=600,
        step=100,
        help="Only applicable for **Text Summary** option",
    )
    submit_button = form.form_submit_button(
        label="Submit", disabled=not st.session_state.valid_key
    )

    if submit_button:
        file_path, file_type = write_uploaded_file(uploaded_file, resume_path)
        extracted_text = ""
        # st.write(file_type)
        if file_type == "application/pdf":
            # Extract PDF text
            extracted_text = extract_text(file_path)
        elif (
            file_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            # Extract DOCX text
            extracted_text = docx2txt.process(file_path)

        if len(extracted_text) != 0:
            if output_type == "Text Summary":
                # Start timer
                start_time = time.time()

                prompt = summarize_cv(extracted_text, word_limit=word_limit)
                gpt_response = st.session_state.gpt.get_completion_from_messages(
                    messages=prompt
                )
                summarized_text = gpt_response.choices[0].message["content"]
                tokens_used = gpt_response.usage.total_tokens

                # End timer
                end_time = time.time()

                # Calculate the execution_time
                exec_time = end_time - start_time
            elif output_type == "JSON Format":
                # Start timer
                start_time = time.time()

                prompt, cv_details_schema = extract_cv_details(
                    resume_context=extracted_text, response_schema=response_schema
                )
                gpt_response = st.session_state.gpt.get_completion_from_messages(
                    messages=prompt, functions=cv_details_schema
                )
                gpt_summary = gpt_response.choices[0].message.function_call.arguments
                tokens_used = gpt_response.usage.total_tokens
                # st.markdown("#### GPT Response:")
                # st.markdown(gpt_summary)
                json_response = json.loads(gpt_summary)

                # End timer
                end_time = time.time()

                # Calculate the execution_time
                exec_time = end_time - start_time


with col2:
    if output_type == "Text Summary" and len(summarized_text) > 0:
        with st.expander(label="", expanded=True):
            st.markdown(f"### {output_type}")
            st.write(summarized_text)
            st.markdown(
                f"<p style='font-size: smaller; color: green;'>Tokens used: {tokens_used}</br>Executed in {exec_time:.4f} seconds",
                unsafe_allow_html=True,
            )
    elif output_type == "JSON Format" and json_response:
        with st.expander(label="", expanded=True):
            st.markdown(f"### {output_type}")
            st.write(json_response)
            st.markdown(
                f"<p style='font-size: smaller; color: green;'>Tokens used: {tokens_used}</br>Executed in {exec_time:.4f} seconds",
                unsafe_allow_html=True,
            )
