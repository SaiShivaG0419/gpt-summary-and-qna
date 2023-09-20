import os
import sys
import shutil
import base64
import streamlit as st
from PIL import Image
from streamlit_extras.switch_page_button import switch_page

# Get the absolute path to the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
src_path = os.path.abspath(os.path.join(project_root, "src"))
sys.path.insert(0, src_path)



#### Set Page Config
def page_config():
    st.set_page_config(
        page_title="GPT Use Cases",
        page_icon="❇️",
        layout="wide",
        menu_items={"About": "A simple web app for various GPT Use Cases"},
    )
    with open("assets/Title-Image-dark-small.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
        st.sidebar.markdown(
        f"""
        <div style="display:table;margin-top:-30%; margin-left: 10%;">
            <img src="data:image/png;base64,{data}" >
        </div>
        """,
        unsafe_allow_html=True,
        )


@st.cache_resource
def custom_css():
    st.markdown(
        """ <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
                        padding-top: 2rem;
                    }
        </style> """,
        unsafe_allow_html=True,
    )


def switch_main():
    if st.sidebar.button("⬅️ Main", use_container_width=True):
        switch_page("main")


def initialization():
    if "page" not in st.session_state:
        st.session_state.page = "main"


def delete_folder_contents(folder_path):
    """A function to delete the folder and it's content"""
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Delete the folder and its contents
        shutil.rmtree(folder_path)
        print(f"Deleted everything in '{folder_path}'.")
    else:
        print(f"Folder '{folder_path}' does not exist.")

def count_files_in_directory(directory):
    """ A function to count files in directory"""
    if not os.path.exists(directory):
        return 0
    
    if not os.path.isdir(directory):
        return 0
    
    file_count = 0
    for _, _, files in os.walk(directory):
        file_count += len(files)
    
    return file_count


def write_uploaded_file(uploaded_file, folder_path):
    """A function to write the file to the folder from streamlit file uploader"""

    if uploaded_file is not None:
        # Create directory if not exists
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        
        return file_path, uploaded_file.type

def write_uploaded_files(uploaded_files, folder_path):
    """A streamlit function to write the multiple files to local directory from streamlit file uploader"""

    len_uploaded_files = len(uploaded_files)

    # Validate files and copy to new_files directory
    if len_uploaded_files != 0:
        try:         
            # Create directory if not exists
            os.makedirs(folder_path, exist_ok=True)
            file_count = 0
            msg = st.toast(f"Uploading {len_uploaded_files} files...")
            for file in uploaded_files:
                # Save the file to new_files directory
                file_path = os.path.join(folder_path, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.read())
                file_count += 1
                # Display a success message after upload is done
                msg.toast(f"Uploaded {file_count}/{len_uploaded_files} files: {file.name}")

            if file_count == len_uploaded_files:
                st.success("All files uploaded and validated successfully.")
                msg.toast(f"Upload Complete.", icon="✔️")
                upload_success = True
            elif file_count > 0 and file_count <= len_uploaded_files:
                st.warning(f"Only {file_count} out of {len_uploaded_files} files are uploaded.")
                msg.toast(f"Upload Complete.", icon="⚠️")
                upload_success = True
            else:
                st.error("No files are uploaded.")
                msg.toast(f"Upload Error.", icon="❌")
                upload_success = False

        except Exception as e:
            error_msg = f"An error occurred while uploading files: {e}"
            st.exception(error_msg)
            upload_success = False
    else:
        st.error("Please add the files first.")
        upload_success = False
    
    return upload_success
