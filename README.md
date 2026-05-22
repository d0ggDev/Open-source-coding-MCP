# Specialized Model Code Generation Pipeline

A cost-effective, high-quality code generation pipeline using local models (Ollama) and cloud validation (Claude Sonnet).

## Features
- **Cost-Optimized**: Uses local LLMs (DeepSeek-R1, Qwen2.5-Coder, Mistral) for 90% of tasks.
- **Orchestrated**: Managed by LangGraph state machine.
- **Ready for Extensions**: Modular architecture.

## Getting Started

### Prerequisites
- [Ollama](https://ollama.com/) running.
- Python 3.10+.

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Install dependencies
pip install langgraph anthropic requests

# Pull required models
ollama pull deepseek-r1:7b-qwen-distill-q4_0
ollama pull qwen2.5-coder:7b
ollama pull mistral:7b-q4_0

# Set API key
export ANTHROPIC_API_KEY="your-key-here"
```

## Documentation
Check the `docs/` folder for setup guides and architecture details.

## Running the Pipeline
```bash
python doggy_ai.py build "Create a simple calculator in Python"
```

## License
MIT
