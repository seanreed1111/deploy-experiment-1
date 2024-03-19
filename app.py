import os, json
from pprint import pprint
from pathlib import Path
from loguru import logger
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import ChatMessage
# from langchain_openai import ChatOpenAI
from langchain_community.chat_models.azure_openai import AzureChatOpenAI #deprecated class, fix later
import streamlit as st
st.set_option('server.enableCORS', True)
LANGCHAIN_PROJECT = "Deploy #1: Chat with Azure OpenAI"
st.set_page_config(page_title=LANGCHAIN_PROJECT, page_icon="")
st.title(LANGCHAIN_PROJECT)

# def run_config():
#     config_dir = Path("content")
#     openai_config_file_path = config_dir / "allconfig.json"
#     config_files = [openai_config_file_path]
#     config = {}
#     for file in config_files:
#         with open(file) as json_config:
#             config.update(json.load(json_config))
#     for k in config:
#         os.environ[k] = config[k]

os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT

# with st.sidebar:
#     config_load_state = st.text('Loading config...')
#     run_config()
#     config_load_state.text('Loading config...done!')


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)


# with st.sidebar:
#     openai_api_key = st.text_input("OpenAI API Key", type="password")

if "messages" not in st.session_state:
    st.session_state["messages"] = [ChatMessage(role="assistant", content="How can I help you?")]

for msg in st.session_state.messages:
    st.chat_message(msg.role).write(msg.content)

if prompt := st.chat_input():
    st.session_state.messages.append(ChatMessage(role="user", content=prompt))
    st.chat_message("user").write(prompt)

    # if not openai_api_key:
    #     st.info("Please add your OpenAI API key to continue.")
    #     st.stop()

    with st.chat_message("assistant"):
        stream_handler = StreamHandler(st.empty())
        llm = AzureChatOpenAI(
            temperature=0,
            streaming=True,
            max_tokens=300,
            azure_deployment=os.environ["AZURE_OPENAI_API_DEPLOYMENT_NAME"],
            azure_endpoint=os.environ["AZURE_OPENAI_API_ENDPOINT"],
            model_name=os.environ["MODEL_NAME"],
            openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            request_timeout=45,
            verbose=True,
            callbacks=[stream_handler]
        )
        
        response = llm.invoke(st.session_state.messages)
        st.session_state.messages.append(ChatMessage(role="assistant", content=response.content))
