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

################# Streamlit Implementation #################

st.set_page_config(page_title="Code GPT", page_icon="🦜")
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

    for msg in st.session_state.messages:
        if msg['role'] == "assistant":
            if msg['content'] == "Hi, I'm here to help you code 🚀":
                st.chat_message(msg['role']).write(msg['content'])
            else:
                st.chat_message(msg['role']).code(msg['content'])
                with st.expander("Execute function"):
                    st.code(msg['expander_content'])
        else:
            st.chat_message(msg['role']).write(msg['content'])

    if user_input := st.chat_input(placeholder='Start asking your codes here..'):
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        st.chat_message('user').write(user_input)

    if st.session_state.messages[-1]['role']!='assistant':
        with st.chat_message('assistant'):
            with st.spinner('Generating response..'):
                response = get_llm_response(user_input, with_message_history, config)
                code = clean_generated_code(response)
                st.code(code)

                extracted_function = extract_function(code)
                function_name = extract_function_name(code)

                st.session_state.code = code
                st.session_state.extracted_function = extracted_function
                st.session_state.function_name = function_name

                input_vars_dict = retrieve_input_vars_and_type(code)

                expander = st.expander("Execute function")
                expander.code(f'Output of the code: {run_code(code)[1]}')

                #st.session_state.expander= expander
                user_input = expander.text_input("Enter input vars separated by space")
                #if user_input:
                user_input = user_input.strip()
                input_dtypes = list(input_vars_dict.values())
                try:
                    final_user_input = parse_user_input(user_input, input_dtypes)
                except Exception as e:
                    st.error(f"Error parsing inputs: {str(e)}")
                    final_user_input = None

                local_vars = {}
                exec(function_name)
                try:
                    expander_response = call_function_by_name(function_name, *user_input)
                    st.code(expander_response)
                    st.session_state.output = expander_response
                except Exception as e:
                    st.session_state.output = str(e)

        st.session_state.messages.append({'role': 'assistant', 'content': code, 'expander_content':st.session_state.output})

    # # This ensures that the messages persist and append correctly
    # st.session_state.messages = st.session_state.messages

    #python program to find the square of a number


    # Display the output if it exists
    # if "extracted_function" in st.session_state:
    #     st.code(st.session_state.extracted_function)

    #     with st.expander("Run Your Function"):
    #         custom_input = st.number_input("Custom values", value=0)

    #         # Prepare to execute the function stored in session_state
    #         local_vars = {}
    #         exec(st.session_state.extracted_function, {}, local_vars)
    #         user_response = local_vars[st.session_state.function_name](custom_input)
    #         st.code(user_response)

            
    st.sidebar.button('Clear Chat History', on_click=reset_chat(session_id))