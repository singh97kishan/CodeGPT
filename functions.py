def random_session_id(length: int):
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_session_history(session_id: str):
    import streamlit as st
    from langchain_community.chat_message_histories import ChatMessageHistory
    if session_id not in st.session_state.store:
        st.session_state.store[session_id] = ChatMessageHistory()
    return st.session_state.store[session_id]

def get_llm_response(user_prompt, with_message_history, config):
    from langchain_core.messages import HumanMessage
    response = with_message_history.invoke(
        [HumanMessage(content=user_prompt)],
        config=config
    )
    return response.content

def clean_generated_code(response):
    import re
    code_blocks = re.findall(r'```python(.*?)```', response, re.DOTALL)
    extracted_code = '\n'.join(block.strip() for block in code_blocks)
    return extracted_code


def extract_missing_modules(error_msg):
    missing_modules = re.findall(r"ModuleNotFoundError: No module named '(\w+)'", error_msg)
    return missing_modules

def install_module(module_name):
    import subprocess
    result = subprocess.run(["pip", "install", module_name], check=True)
    if result.returncode == 0:
        print(f"Module '{module_name}' installed successfully")
    else:
        print(f"Failed to install module '{module_name}'")
    return result.returncode == 0

def run_code(code):
    import subprocess, sys
    try:
        result = subprocess.run([f"{sys.executable}", "-c", code], capture_output=True, text=True, timeout=3000)
        if result.returncode != 0:
            missing_modules = extract_missing_modules(result.stderr)
            for module in missing_modules:
                install_module(module)
            result = subprocess.run([f"{sys.executable}", "-c", code], capture_output=True, text=True, timeout=3000)
            if result.returncode != 0:
                return False, result.stderr
        else:
            return True, result.stdout
    except subprocess.TimeoutExpired:
        return False, "Execution timed out"
    except Exception as e:
        return False, str(e)

def extract_function(code_string):
    lines = code_string.splitlines()
    function_lines = []
    inside_function = False
    indentation_level = None

    for line in lines:
        if line.strip().startswith("def "):
            inside_function = True
            function_lines.append(line)
            indentation_level = len(line) - len(line.lstrip())
        elif inside_function:
            current_indentation = len(line) - len(line.lstrip())
            if current_indentation <= indentation_level and line.strip() != "":
                break
            function_lines.append(line)
    return "\n".join(function_lines)

def extract_function_name(code_string):
    import re
    match = re.search(r'def\s+(\w+)\s*\(', code_string)
    if match:
        return match.group(1)
    return None

def call_function_by_name(function_name, *args, **kwargs):
    if function_name in globals():
        return globals()[function_name](*args, **kwargs)
    elif function_name in locals():
        return locals()[function_name](*args, **kwargs)
    else:
        raise NameError(f"Function '{function_name}' is not defined.")

def reset_chat(session_id):
    import streamlit as st
    st.session_state.messages = [{"role": "assistant", "content": "Hi, I'm here to help you code 🚀"}]
    st.session_state.generated_code = None
    st.session_state.output = None
    st.session_state.store[session_id] = None

def retrieve_input_vars_and_type(code_string: str) -> dict:
    import re
    input_params_pattern = r"def\s+\w+\(([^)]+)\)"
    input_type_pattern = r"(\w+):\s*(\w+)"
    input_params_match = re.search(input_params_pattern, code_string)
    if input_params_match:
        input_params = input_params_match.group(1).strip()
        input_vars = re.findall(input_type_pattern, input_params)
        input_dict = {var: type_ for var, type_ in input_vars}
        return input_dict

def parse_user_input(user_input, type_mapping):
    input_values = user_input.split(' ')
    if len(input_values) != len(type_mapping):
        raise ValueError("Number of input values does not match the number of expected types.")
    converted_values = []
    for value, dtype in zip(input_values, type_mapping):
        if dtype == 'float':
            converted_values.append(float(value))
        elif dtype == 'int':
            converted_values.append(int(value))
        elif dtype == 'str':
            converted_values.append(value)
        elif dtype == 'bool':
            converted_values.append(value.lower() in ['true', '1', 'yes'])
        else:
            raise ValueError(f"Unsupported data type: {dtype}")
    return tuple(converted_values)