import streamlit as st
import ollama
import time

# App title must be the first command
st.set_page_config(page_title="Ollama Chat", page_icon="💬", layout="wide")

# Hide the native Streamlit navigation
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# Main title
st.title("💬 Ollama Chat")
st.write("Chat with your Ollama models")

# Navigation at the bottom of the sidebar
st.sidebar.divider()
if st.sidebar.button("🏠 Go to Model Manager", use_container_width=True):
    st.switch_page("app.py")

# Sidebar: Subheader for models and parameters
st.sidebar.subheader("Models and parameters")

# Initialize the Ollama client and fetch available models
def get_client():
    host = st.session_state.get('ollama_host', 'http://localhost:11434')
    return ollama.Client(host=host)

# Host configuration
host_url = st.sidebar.text_input("Ollama host URL", value="http://localhost:11434")
if st.sidebar.button("Save Configuration"):
    st.session_state['ollama_host'] = host_url
    st.rerun()

try:
    agent = get_client()
    models_response = agent.list()
    available_models = [model["model"] for model in models_response["models"]]
    selected_model = st.sidebar.selectbox(
        "Choose your model", 
        available_models, 
        index=available_models.index("llama3:latest") if "llama3:latest" in available_models else 0
    )
except Exception as e:
    st.sidebar.error(f"Failed to fetch models: {str(e)}")
    available_models = []
    selected_model = None

# Sidebar: Model parameters
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
mirostat_tau = st.sidebar.slider("Mirostat Tau", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
num_ctx = st.sidebar.slider("Num Context", min_value=512, max_value=8192, value=4096, step=1)
top_p = st.sidebar.slider("Top P", min_value=0.0, max_value=1.0, value=0.9, step=0.01)
top_k = st.sidebar.slider("Top K", min_value=0, max_value=500, value=40, step=1)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Function to clear chat history
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button("Clear Chat History", on_click=clear_chat_history)

# Sidebar: Custom system prompt
with st.sidebar.expander("Customize System Prompt"):
    custom_system_prompt = st.text_area(
        "Prompt",
        value="You are a helpful assistant. Your responsibility is to assist your user to the best of your ability. You must be helpful and direct in your communication."
    )

# Function for generating response using Ollama with streaming
def generate_response_with_ollama(prompt_input):
    messages = [
        {"role": "system", "content": custom_system_prompt},
        {"role": "assistant", "content": "Hello, I am your personal AI assistant. How can I help you today?"}
    ]
    messages.extend(st.session_state.messages)
    messages.append({"role": "user", "content": prompt_input})
    
    if selected_model:
        for response in agent.chat(
            model=selected_model.lower(),
            messages=messages,
            stream=True,
            options={
                "temperature": temperature,
                "mirostat_tau": mirostat_tau,
                "num_ctx": num_ctx,
                "top_p": top_p,
                "top_k": top_k
            }
        ):
            if "message" in response:
                yield response["message"]["content"]
            if response.get("end_of_message", False):
                break
    else:
        yield "Model not selected or available."

# Chat interface
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Generate response if last message is from user
if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
    message_placeholder = st.empty()
    with st.spinner("Processing..."):
        response_generator = generate_response_with_ollama(prompt)
        full_response = ""
        first_response = True
        for response in response_generator:
            if first_response:
                st.empty()
                first_response = False
            full_response += response
            message_placeholder.chat_message("assistant").write(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})