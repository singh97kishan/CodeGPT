from system_prompt import system_prompt # System prompt
from functions import *
import streamlit as st
import os
import random
import string
import re
import sys
import subprocess
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()

st.set_page_config(page_title="Code GPT", page_icon="🦜", layout='wide')
st.title("Code GPT")

st.sidebar.title("Model Settings")
radio_options = ['Self Groq API Key', 'Default Groq API Key']
selected_radio_option = st.sidebar.radio(options=radio_options, label="Groq API Key")
if selected_radio_option == 'Self Groq API Key':
    groq_api_key = st.sidebar.text_input("Groq API Key", type="password")
else:
    groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.info("Enter Groq API Key to proceed")
else:
    llm = ChatGroq(model_name="Mixtral-8x7b-32768", groq_api_key=groq_api_key)

    session_id = random_session_id(5)
    config = {"configurable": {"session_id": f"{session_id}"}}

    if "store" not in st.session_state:
        st.session_state.store = {}

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi, I'm here to help you code 🚀"}
        ]

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="user_message")
        ]
    )

    chain = prompt | llm
    with_message_history = RunnableWithMessageHistory(chain, get_session_history)

    user_query= st.text_area("Start asking your codes here..")
    if st.button("Submit query"):
        with st.spinner("Generating code..."):
            response = get_llm_response(user_query, with_message_history, config)
            code = clean_generated_code(response)
        st.session_state.code= code

    if 'code' in st.session_state:
        st.subheader("Generated Code:")
        st.code(st.session_state.code, language='python')
        extracted_function = extract_function(st.session_state.code)
        function_name = extract_function_name(st.session_state.code)
        input_vars_dict = retrieve_input_vars_and_type(st.session_state.code)

        st.session_state.function= extracted_function
        st.session_state.function_name= function_name
        st.session_state.func_input_vars = input_vars_dict

        st.code(run_code(st.session_state.code)[1])
        user_input = st.text_input("Enter input vars separated by space")

        if st.button('Run Function'):
            user_input = user_input.strip()
            input_dtypes = list(input_vars_dict.values())
            try:
                final_user_input = parse_user_input(user_input, input_dtypes)
            except Exception as e:
                st.error(f"Error parsing inputs: {str(e)}")
                final_user_input = None
            
            # Execute the function definition in the global context
            exec(st.session_state.function, globals())
            
            try:
                # Retrieve and call the function directly from globals
                function_to_call = globals().get(st.session_state.function_name)
                if function_to_call is None:
                    raise NameError(f"Function '{st.session_state.function_name}' is not defined.")
                
                final_response = function_to_call(*final_user_input)
                st.code(final_response)
            except NameError as e:
                st.error(f"Error: {str(e)}")
            except Exception as e:
                st.error(f"Error during function execution: {str(e)}")


    st.sidebar.button('Clear Chat History', on_click=reset_chat(session_id))
