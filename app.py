import os
import openai
import streamlit as st
import streamlit.components.v1 as components
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.chains.llm_symbolic_math.base import LLMSymbolicMathChain
import re

#######
#from dotenv import load_dotenv, find_dotenv
#load_dotenv(find_dotenv())
#######

st.sidebar.title("Cleo, The Math Solver")
st.sidebar.image("Cleo.png", width=100)

html1="""
<a href='https://ko-fi.com/S6S3C06PD' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi1.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
<br />
<a href="https://twitter.com/alonsosilva?ref_src=twsrc%5Etfw" class="twitter-follow-button" data-show-count="false">Follow @alonsosilva</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
"""

st.sidebar.write("Examples:")
Example1 = st.sidebar.button("What's the integral of 1/(x^3+1)?")
Example2 = st.sidebar.button("What's the derivative of sin(x)*exp(x)?")
Example3 = st.sidebar.button("What are the solutions to the equation y^3 + 1/3y?")
Example4 = st.sidebar.button("""Solve the differential equation y"(t) - y(t) = e^t with respect to t""")

with st.sidebar:
    components.html(html1)

# html2="""
# <script async defer src="https://buttons.github.io/buttons.js"></script>
# """
# html3="""
# <a class="github-button" href="https://github.com/alonsosilvaallende/chloe-streamlit" data-color-scheme="no-preference: light; light: light; dark: dark;" data-icon="octicon-star" data-show-count="true" aria-label="Star alonsosilvaallende/chloe-streamlit on GitHub">Star</a>
# """
# 
# st.sidebar.markdown(html2, unsafe_allow_html=True)
# st.sidebar.markdown(html3, unsafe_allow_html=True)

openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENROUTER_API_KEY")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_REFERRER = "https://github.com/alonsosilvaallende/langchain-streamlit"

llm = ChatOpenAI(model_name="google/palm-2-chat-bison",
                 temperature=0.1,
                 headers={"HTTP-Referer": OPENROUTER_REFERRER})

llm_symbolic_math = LLMSymbolicMathChain.from_llm(llm)

@st.cache_resource
def aux():
    memory = ConversationBufferMemory(return_messages=True)
    conversation = ConversationChain(memory=memory, llm=llm)
    return memory, conversation
 
memory, conversation = aux()

def string2latex(resultado):
    resultado = resultado.split("Answer: ")[-1]
    strings_to_replace = {
        'log': "\log",
        "exp": "\exp",
        "sqrt": "\sqrt",
        "atan": "\\arctan",
        "asin": "\\arcsin",
        "acos": "\\arccos",
        "**": "^",
        "I": "i"
    }
    for key, value in strings_to_replace.items():
        resultado = resultado.replace(key, value)
    resultado, n = re.subn('^sin|[^c]sin', 'backslash_sin', resultado)
    resultado, n = re.subn('^cos|[^c]cos', 'backslash_cos', resultado)
    resultado, n = re.subn('^tan|[^c]tan', 'backslash_tan', resultado)
    resultado = resultado.replace("backslash_sin","\sin")
    resultado = resultado.replace("backslash_cos","\cos")
    resultado = resultado.replace("backslash_tan","\\tan")
    resultado = re.sub(r'Eq\((.*),(.*)\)',r'\1 = \2' , resultado)
    resultado = re.sub(r'sqrt\(([0-9|i]*)\)', r'sqrt{\1}' , resultado)
    resultado = f"${resultado}$"
    return resultado

def my_evaluator(prompt):
    return llm.predict("""\
Translate a math problem into a expression that can be executed using Python's numexpr library. Use the output of running this code to answer the question.

Question: ${Question with math problem.}
```text
${single line mathematical expression that solves the problem}
```
...numexpr.evaluate(text)...
```output
${Output of running the code}
```
Answer: ${Answer}

Begin.

Question: What is 37593 * 67?
```text
37593 * 67
```
...numexpr.evaluate("37593 * 67")...
```output
2518731
```
Answer: 2518731

Question: 37593^(1/5)
```text
37593**(1/5)
```
...numexpr.evaluate("37593**(1/5)")...
```output
8.222831614237718
```
Answer: 8.222831614237718

Question:""" + prompt)

def my_classifier(prompt):
    return llm.predict("""\
Answer either 1 or 2. Is the following question related to 
1: Evaluating an algebraic expression or 
2: Solve a symbolic expression:
"""+prompt)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input or one of the examples
if (prompt := st.chat_input("Your message")) or Example1 or Example2  or Example3 or Example4:
    if Example1:
        prompt = "What's the integral of 1/(x^3+1)?"
    if Example2:
        prompt = "What's the derivative of sin(x)*exp(x)?"
    if Example3:
        prompt = "What are the solutions to the equation y^3 + 1/3y?"
    if Example4:
        prompt = r"""Solve the differential equation y"(t) - y(t) = e^t with respect to t"""
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        question_class = my_classifier(prompt)
        if '2' in question_class:
            try:
                full_response = llm_symbolic_math.run(prompt)
            except ValueError as e_val:
                st.write(f"Unexpected {e_val}")
                full_response = ""
            except Exception as e_msg:
                st.write(f"Unexpected {e_msg}, {type(e_msg)}")
                full_response = ""
            message_placeholder.markdown(string2latex(full_response))
        elif '1' in question_class:
            try:
                full_response = my_evaluator(prompt)
            except ValueError as e_val:
                st.write(f"Unexpected {e_val}")
                full_response = ""
            except Exception as e_msg:
                st.write(f"Unexpected {e_msg}, {type(e_msg)}")
                full_response = ""
            message_placeholder.markdown(string2latex(full_response))
        else:
            full_response = ""
            st.write(f"Unexpected error")
            message_placeholder.markdown(string2latex(full_response))

    st.session_state.messages.append({"role": "assistant", "content": string2latex(full_response)})
