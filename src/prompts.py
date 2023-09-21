""" A python file to define prompts for various tasks with GPT models"""

from langchain.prompts import PromptTemplate


def summarize_cv(resume_context: str, word_limit: int = 250):
    """A prompt template to summariza the CV content."""
    delimitter = "####"
    system_message = f"""You are an intelligent talent recruiting professional. \
        You require to read through the resume content provided in between {delimitter} characters. \
        You must extract key information from the resume content and provide a quick summary with in {word_limit} words. \
        The summary must focus on following information: \
            1. Overall years of experience and current job information. \
            2. Key domain or industry experience and few key technical skills. \
            3. Key information about past roles and carried responsibilities. \
            4. Highest academic information along with GPA or percentage. \
            5. Highlight if any courses or certifications mentioned. If not, mention no information provided on certifications or courses. \
            6. Key personal information. \
        
        """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"{delimitter}{resume_context}{delimitter}"},
        {"role": "assistant", "content": "Summarized CV Content:\n"},
    ]

    return messages


def summarize_text(text_input: str, word_limit: int = 250):
    """A prompt template to summarize the given text content."""
    delimitter = "####"
    system_message = f"""You are an helpful assistant and follows given instructions. \
        Summarize the text content provided in between {delimitter} characters. \
        Summarized content should be not more than {word_limit} words. \
        Summarized content must has key points present in the provided text.
        """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"{delimitter}{text_input}{delimitter}"},
        {"role": "assistant", "content": "Helpful Summarized content:\n"},
    ]

    return messages


def extract_cv_details(resume_context, response_schema):
    """A prompt template to extract CV content in Json format."""
    delimitter = "####"
    system_message = f"""You are an intelligent talent recrutting professional. \
        You require to read through the resume content provided in between {delimitter} characters. \
        You must extract key information from the resume content and answer in JSON format mentioned in function schema. \
        Date Of Birth format must be DD-MM-YYYY. \
        When end-time of a work experience is present then replace with current Month and year in Month, YYYY format. \
        Don't make assumptions about what values to plug into functions. \
        You must evaluate yourself and verify whether the information is extracted is correct or not. \
        You must not provide any other information that is not requested. \
        
        """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"{delimitter}{resume_context}{delimitter}"},
    ]
    functions = [{"name": "json_response", "parameters": response_schema}]

    return messages, functions


def prompt_doc_qa():
    """A prompt template to define a prompt template for Question and Answering of a document."""

    template = """Use the following pieces of context and answer the question at the end. \
        If you don't know the answer, just say you don't know. \
        Do not try to make up an answer. \
        Follow the query instructions carefully while answering the query. \
        Use maximum of ten sentences if user does not provide any limitation on completion length. \
        Keep the answer concise as possible and should be helpful. \
        Answer should not contain any harmful language. \
        Context: {context} \
        Question: {question} \
        Helpful Answer: \
        """

    qa_chain_prompt = PromptTemplate(
        input_variables=["context", "question"], template=template
    )

    return qa_chain_prompt
