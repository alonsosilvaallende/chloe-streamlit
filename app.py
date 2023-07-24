import openai
import streamlit as st

#######
#from dotenv import load_dotenv, find_dotenv
#load_dotenv(find_dotenv())
#######

st.sidebar.title("Chloe")
#st.sidebar.image("Partido_Republicano.png", width=100)

st.sidebar.write("Examples:")
Example1 = st.sidebar.button("What's the integral of 1/(x^3+1)?")
Example2 = st.sidebar.button("What's the derivative of sin(x)*exp(x)?")
Example3 = st.sidebar.button("What are the solutions to the equation y^3 + 1/3y?")
Example4 = st.sidebar.button("""Solve the differential equation y"(t) - y(t) = e^t with respect to t""")

st.sidebar.markdown("If you can, [buy me a coffee](https://bmc.link/alonsosilva)")
st.sidebar.markdown("Follow me on [Twitter (alonsosilva)](https://twitter.com/alonsosilva)")

import os
import openai
from langchain.chat_models import ChatOpenAI
from langchain.chains.llm_symbolic_math.base import LLMSymbolicMathChain

openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENROUTER_API_KEY")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_REFERRER = "https://github.com/alonsosilvaallende/langchain-streamlit"



llm = ChatOpenAI(model_name="google/palm-2-chat-bison",
                 temperature=0.1,
                 headers={"HTTP-Referer": OPENROUTER_REFERRER})


llm_symbolic_math = LLMSymbolicMathChain.from_llm(llm)

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

@st.cache_resource
def aux():
    memory = ConversationBufferMemory(return_messages=True)
    conversation = ConversationChain(memory=memory, llm=llm)
    return memory, conversation
 
memory, conversation = aux()

def string2latex(resultado):
    strings_to_replace = {
        "Answer: ": "",
        'log': "\log",
        "exp": "\exp",
        "sqrt": "\sqrt",
        "sin": "\sin",
        "cos": "\cos",
        "atan": "arctan",
        "**": "^",
        "I": "i"
    }
    for key, value in strings_to_replace.items():

        resultado = resultado.replace(key, value)
    resultado = f"${resultado}$"
    return resultado

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
        full_response = llm_symbolic_math.run(prompt)
        message_placeholder.markdown(string2latex(full_response))
    st.session_state.messages.append({"role": "assistant", "content": string2latex(full_response)})
