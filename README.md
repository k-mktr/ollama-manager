# Simple Ollama Manager & Chat Interface

## Overview

This project provides a Streamlit-based interface for managing Ollama models and chatting with them. It consists of two main components:

1. **Model Manager**: A comprehensive interface for managing Ollama models, including:
   - Viewing installed models
   - Pulling new models
   - Updating existing models
   - Deleting models
   - Viewing model details
   - System resource monitoring

2. **Chat Interface**: A conversational interface that allows you to:
   - Select from available Ollama models
   - Configure model parameters
   - Chat with the selected model
   - Customize system prompts
   - Clear chat history

## Features

### Model Manager
- 🗂️ View all installed models with detailed information
- 🔄 Update existing models to latest versions
- 🗑️ Delete unwanted models
- 📥 Pull new models from Ollama repository
- 📊 View system resource usage (disk space)
- 🔍 Search and filter models
- 📝 View detailed model information

### Chat Interface
- 💬 Chat with selected Ollama models
- ⚙️ Configure model parameters:
  - Temperature
  - Mirostat Tau
  - Context Window Size
  - Top P
  - Top K
- 📝 Customize system prompt
- 🧹 Clear chat history
- 🔄 Switch between different models
- 🌐 Configure Ollama host URL

## Requirements

- Python 3.8+
- Streamlit
- Ollama Python client
- Running Ollama server

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/k-mktr/ollama-manager.git
   cd ollama-manager
   ```

2. Install dependencies:
   ```bash
   pip install ollama streamlit -U
   ```

3. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Model Manager**:
   - Access the model manager by running `app.py`
   - Use the sidebar to pull new models or configure settings
   - Manage existing models using the action buttons (Update, Delete, Details)

2. **Chat Interface**:
   - Access the chat interface by running `chat.py` or clicking "Go to Chat" in the Model Manager
   - Select a model from the sidebar
   - Configure model parameters as needed
   - Start chatting in the main interface

## Configuration

- **Ollama Host**: Configure the Ollama server URL in the sidebar of either interface
- **System Prompt**: Customize the system prompt in the Chat Interface sidebar

## Navigation

- Use the sidebar buttons to switch between the Model Manager and Chat Interface
- Changes made in one interface are reflected in the other

## License

MIT License
