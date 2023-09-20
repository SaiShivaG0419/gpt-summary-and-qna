# GPT Use Cases
Summarization and QnA use cases using Open AI's GPT models. 

To use this application, you must create an API Key with Open AI and pass it as an env variable. The steps are mentioned below:

1. Rename the file '.sample-env' to '.env' in the project root directory or create a '.env' file with same contents as '.sample-env' file.
2. Update the 'OPENAI_API_KEY' value with your API Key and save the file.
    
3. In your terminal, create an virtual environment and install requirements from requirements file by running following command.

   `python -m pip install -r requirements.txt --no-cache-dir`
4. Run following command from the project root directory to launch the streamlit application.

   `streamlit run frontend/main.py`
5. Browse `http://localhost:8501/` to see the application.
6. Optionally, you can build a docker image and deploy as a container after step 2.
7. To build, docker image, execute following in the project root directory.

    `docker build -t gpt-summary-qna .`
8. To run, the container, execute the command: `docker run -d -p 80:8501 gpt-summary-qna`

