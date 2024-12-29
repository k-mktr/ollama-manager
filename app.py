import streamlit as st
import ollama
from typing import Dict, List
from datetime import datetime
import time

# Enable wide mode
st.set_page_config(layout="wide", page_title="Ollama Model Manager")

def get_client() -> ollama.Client:
    """Get Ollama client with configured host"""
    host = st.session_state.get('ollama_host', 'http://localhost:11434')
    return ollama.Client(host=host)

def load_models() -> Dict:
    """Load models from Ollama client"""
    try:
        client = get_client()
        return client.list()
    except Exception as e:
        st.error(f"Failed to load models: {str(e)}")
        return {}

def delete_model(model_name: str) -> None:
    """Delete a model using Ollama client"""
    try:
        client = get_client()
        with st.spinner(f"Deleting {model_name}..."):
            client.delete(model_name)
        st.toast(f"✅ Successfully deleted {model_name}", icon="✅")
        st.success(f"Successfully deleted {model_name}")
        time.sleep(2)
        st.rerun()
    except Exception as e:
        st.error(f"Error deleting model {model_name}: {str(e)}")

def update_model(model_name: str) -> None:
    """Update (re-pull) a model using Ollama client"""
    try:
        client = get_client()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner(f"Updating {model_name}..."):
            # Get the streaming response
            response_gen = client.pull(model_name, stream=True)
            
            # Process the streamed response
            for response in response_gen:
                if 'completed' in response and 'total' in response:
                    progress = response['completed'] / response['total']
                    progress_bar.progress(progress)
                    status_text.text(f"Downloading {response['completed']}/{response['total']} bytes")
        
        st.toast(f"✅ Successfully updated {model_name}", icon="✅")
        st.success(f"Successfully updated {model_name}")
        time.sleep(2)  # Wait for 2 seconds before rerun
        st.rerun()
    except Exception as e:
        st.error(f"Error updating model {model_name}: {str(e)}")

def calculate_total_disk_space(models: list) -> float:
    """Calculate total disk space used by models"""
    return sum(model.get("size", 0) for model in models)

def pull_new_model(model_name: str) -> None:
    """Pull a new model using Ollama client"""
    try:
        client = get_client()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner(f"Pulling {model_name}..."):
            response_gen = client.pull(model_name, stream=True)
            
            for response in response_gen:
                if 'completed' in response and 'total' in response:
                    progress = response['completed'] / response['total']
                    progress_bar.progress(progress)
                    status_text.text(f"Downloading {response['completed']}/{response['total']} bytes")
        
        st.success(f"Successfully pulled {model_name}")
        st.rerun()  # Refresh the page to update the model list
    except Exception as e:
        st.error(f"Error pulling model {model_name}: {str(e)}")

def get_model_details(model_name: str) -> Dict:
    """Get detailed information about a specific model"""
    try:
        client = get_client()
        return client.show(model_name)
    except Exception as e:
        st.error(f"Error getting details for {model_name}: {str(e)}")
        return {}

def main():
    st.title("Ollama Model Manager")
    
    # Hide the native Streamlit navigation
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Configuration section - simplified
    st.sidebar.subheader("⚙️ Configuration")
    host = st.sidebar.text_input(
        "Ollama Host",
        value=st.session_state.get('ollama_host', 'http://localhost:11434'),
        help="Enter the URL of your Ollama server (e.g., http://localhost:11434)"
    )
    if st.sidebar.button("Save Configuration"):
        st.session_state['ollama_host'] = host
        st.rerun()
    
    # Pull New Model section
    st.sidebar.subheader("Pull New Model")
    new_model_name = st.sidebar.text_input("Enter model name to pull", placeholder="llama3.2-vision:11b-instruct-q4_K_M")
    if st.sidebar.button("Pull Model", key="pull_new_model_button"):
        if new_model_name.strip():
            pull_new_model(new_model_name)
        else:
            st.error("Please enter a valid model name.")
    
    # Load models
    models_data = load_models()
    models = models_data.get("models", []) if models_data else []
    total_disk_space_gb = calculate_total_disk_space(models) / 1e9 if models else 0
    
    # System Information section with improved formatting
    st.sidebar.divider()
    st.sidebar.subheader("📊 System Information")
    st.sidebar.markdown("**Total Disk Space Used**  \n" + f"{total_disk_space_gb:.2f} GB")
    st.sidebar.markdown("**Installed Models**  \n" + f"{len(models)}")
    
    if models:
        biggest_model = max(models, key=lambda x: x.get("size", 0))
        st.sidebar.markdown("**Largest Model**  \n" + f"{biggest_model['model']}")
        st.sidebar.markdown("**Size**  \n" + f"{biggest_model.get('size', 0) / 1e9:.2f} GB")
    
    # Navigation at the bottom of the sidebar
    st.sidebar.divider()
    if st.sidebar.button("💬 Go to Chat", use_container_width=True):
        st.switch_page("pages/chat.py")
    
    # Main content
    if not models:
        st.warning("No models found. Please ensure the Ollama server is running and accessible.")
        return
    
    st.subheader("Installed Models")
    
    # Search and filter
    search_term = st.text_input("🔍 Search models", placeholder="Filter by name, family, or size...").strip().lower()
    
    # Sort options
    sort_options = {
        "Name": "name",
        "Size": "size",
        "Parameters": "params",
        "Family": "family",
        "Modified": "modified"
    }
    sort_by = st.selectbox("Sort by", list(sort_options.keys()))
    sort_ascending = st.checkbox("Ascending", value=True)
    
    # Apply filtering and sorting
    filtered_models = [
        model for model in models 
        if search_term in model["model"].lower() 
        or (model.get("details", {}).get("family", "").lower() and search_term in model["details"]["family"].lower())
        or (str(model.get("details", {}).get("parameter_size", "")).strip().lower() and search_term in str(model["details"]["parameter_size"]).strip().lower())
    ]
    
    if sort_by:
        sort_key = sort_options[sort_by]
        if sort_key == "name":
            filtered_models.sort(key=lambda x: x["model"].lower(), reverse=not sort_ascending)
        elif sort_key == "size":
            filtered_models.sort(key=lambda x: x.get("size", 0), reverse=not sort_ascending)
        elif sort_key == "params":
            filtered_models.sort(key=lambda x: float(x.get("details", {}).get("parameter_size", "0").rstrip('BMK')), reverse=not sort_ascending)
        elif sort_key == "family":
            filtered_models.sort(key=lambda x: x.get("details", {}).get("family", "").lower(), reverse=not sort_ascending)
        elif sort_key == "modified":
            filtered_models.sort(key=lambda x: x.get("modified_at", ""), reverse=not sort_ascending)

    # Display models in a table
    for model in filtered_models:
        with st.expander(f"{model['model']}"):
            # First row with buttons and basic info
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**Size:** {model.get('size', 0) / 1e9:.2f} GB")
                st.write(f"**Parameters:** {model.get('details', {}).get('parameter_size', 'N/A')}")
                st.write(f"**Family:** {model.get('details', {}).get('family', 'N/A')}")
                
            with col2:
                if st.button("🔄 Update", key=f"update_{model['model']}", use_container_width=True):
                    update_model(model['model'])
                    
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{model['model']}", use_container_width=True):
                    delete_model(model['model'])
                    
            with col4:
                if st.button("📝 Details", key=f"details_{model['model']}", use_container_width=True):
                    st.session_state[f"show_details_{model['model']}"] = True
            
            # Details section - full width
            if st.session_state.get(f"show_details_{model['model']}", False):
                st.write("---")  # Add a separator
                st.write("### Model Details")
                details = get_model_details(model['model'])
                st.json(details, expanded=True)

if __name__ == "__main__":
    main()
