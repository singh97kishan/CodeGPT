### 🚀 **Code GPT**:** Generative AI Python Code Generator**

A powerful AI-based solution that generates Python code based on user input prompts and allows you to execute it right in the UI.


**Overview**
Code GPT is a state-of-the-art Generative AI project designed to create Python programs dynamically from user input prompts. It provides a seamless interface where users can not only generate Python code but also execute it directly within the Streamlit-powered UI. The AI model behind this project leverages Langchain for intelligent prompt understanding, Mixtral from Groq for efficient generative computation, and the robustness of Python for code generation and execution.


🌟 ***Unique Selling Point (USP)***
Unlike typical code generators, Code GPT stands out by allowing users to execute the generated Python code within the Streamlit UI itself. The tool extracts Python functions and runs them without needing to leave the interface or manually copy the code into another environment.

✨ ***Features***
* *Generative AI Model:* Generates Python code based on user-provided prompts.
* *Integrated Execution:* Execute generated code directly in the Streamlit interface.
* *Function Extraction & Execution:* Automatically extracts functions from the generated Python code and runs them using subprocess from sys.
* *User-friendly Interface:* Built with Streamlit for an interactive, real-time coding experience.

📂 ***Tech Stack***
* *Mixtral from Groq:* Efficiently handles generative AI computations for code synthesis.
* *Streamlit:* Provides a modern and sleek UI for interaction and code execution.
* *Langchain:* Powers the prompt-to-code framework, enabling robust natural language processing.
* *Python:* The primary language for code generation and execution.

***🤖 How It Handles Code Execution***
The application uses Python's subprocess module to handle function execution in a secure and isolated manner. The tool extracts Python functions from the generated code, sends user inputs to those functions, and then executes them right from the Streamlit app, providing instant feedback.



        