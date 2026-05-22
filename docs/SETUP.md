# Setup Guide

This document provides step-by-step instructions for setting up and running the Specialized Model Code Generation Pipeline.

## 1. Prerequisites

### Software
- **Python 3.10+**: Ensure you have Python installed.
- **Ollama**: [Download and install Ollama](https://ollama.com/) to run local models.

### Models
Run the following commands in your terminal to pull the necessary models:
```bash
ollama pull deepseek-r1:7b-qwen-distill-q4_0
ollama pull qwen2.5-coder:7b
ollama pull mistral:7b-q4_0
```

## 2. Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install dependencies**:
   ```bash
   pip install langgraph anthropic requests
   ```

## 3. Configuration

Set your Anthropic API Key as an environment variable to enable cloud-based validation:

- **Linux/macOS**:
  ```bash
  export ANTHROPIC_API_KEY="your-key-here"
  ```
- **Windows (PowerShell)**:
  ```powershell
  $env:ANTHROPIC_API_KEY="your-key-here"
  ```

## 4. Running the Pipeline

You can use the CLI wrapper to initiate tasks:

```bash
# To initiate a build
python doggy_ai.py build "Requirement string"

# To check status
python doggy_ai.py status
```

## 5. Troubleshooting
- **Ensure Ollama is running**: Check `ollama list` to confirm models are downloaded and the service is active.
- **API Key**: If the pipeline fails at the Review stage, ensure your `ANTHROPIC_API_KEY` is correctly set and has remaining credits.
- **Logs**: Check console output for detailed step-by-step processing.
