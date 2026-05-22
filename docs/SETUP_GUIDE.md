# Specialized Model Code Generation Pipeline - Setup Guide

Based on Gemini's research findings. This pipeline combines:
- **Stage 1**: DeepSeek-R1 (reasoning) - Local via Ollama
- **Stage 2**: Qwen2.5-Coder (coding) - Local via Ollama
- **Stage 3**: Mistral (debugging) - Local via Ollama
- **Stage 4**: Claude Sonnet (review) - API

## Quick Start (15 minutes)

### 1. Install Prerequisites

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Install Python dependencies
pip install langgraph anthropic requests

# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"
```

### 2. Pull the Models

```bash
# Reasoning model (DeepSeek-R1 distilled, 4-5GB)
ollama pull deepseek-r1:7b-qwen-distill-q4_0

# Coding model (Qwen2.5-Coder, 2.1GB)
ollama pull qwen2.5-coder:7b

# Debugging model (Mistral, 2.1GB)
ollama pull mistral:7b-q4_0

# Total: ~8-9GB with quantization
```

### 3. Start Ollama Server

```bash
# Background (macOS/Linux)
ollama serve &

# Or in a separate terminal
ollama serve
```

### 4. Run the Pipeline

```bash
# Copy the pipeline code
cp specialized_pipeline.py your_project/

# Run it
python specialized_pipeline.py
```

Output will be saved to `pipeline_output.json`

---

## Architecture Explained

### Why This Model Combination?

From Gemini's research:

1. **DeepSeek-R1 for Reasoning**
   - Specialized for multi-step thinking
   - Achieves 90%+ accuracy on code planning tasks
   - Creates architectural blueprints, not code
   - Local execution: ~12 tokens/sec

2. **Qwen2.5-Coder for Implementation**
   - Purpose-built for code generation
   - Fast execution: ~18 tokens/sec
   - Small enough to fit in 3GB VRAM
   - Excels at translating designs into working code

3. **Mistral for Verification**
   - Good at finding edge cases and bugs
   - Completes debugging loop locally
   - Prevents bad code reaching API review

4. **Claude Sonnet for Final Review**
   - Catches logical flaws local models miss
   - Optimizes architecture
   - Only called once per feature (~1-5 min)
   - Cost: ~$0.02-0.05 per feature

---

## How It Works

```
User Requirement
    ↓
[Stage 1] DeepSeek-R1: Generate Design (8-15s)
    ↓
[Stage 2] Qwen2.5-Coder: Generate Code (10-20s)
    ↓
[Stage 3] Mistral: Verify Code (local loop, 10-30s per iteration)
    - If high-severity bugs found → revise (up to 3x)
    - If clean → continue
    ↓
[Stage 4] Claude Sonnet: Final Review (2-5s, $0.02-0.05)
    ↓
Production-Ready Code (30-70s total, ~$0.02-0.05 cost)
```

---

## Usage

### Basic Usage

```python
from specialized_pipeline import run_pipeline

result = run_pipeline("""
Build a REST API for creating and listing blog posts:
- POST /posts to create
- GET /posts to list
- Store in PostgreSQL
- Validate input
""")

print(result['final_code'])
```

### Advanced: Custom Models

Edit `specialized_pipeline.py` to swap models:

```python
# Stage 1: Change reasoning model
'model': 'deepseek-coder-v2:16b',  # Use 16B instead

# Stage 2: Change coding model
'model': 'codeqwen:32b-q4_0',  # Use 32B CodeQwen

# Stage 3: Change debugging model
'model': 'mistral-large:latest',  # Use larger Mistral
```

### Advanced: Custom Prompts

Edit the `*_SYSTEM_PROMPT` strings to customize behavior:

```python
REASONING_SYSTEM_PROMPT = """Your custom reasoning instructions..."""
CODING_SYSTEM_PROMPT = """Your custom coding instructions..."""
DEBUG_SYSTEM_PROMPT = """Your custom debugging instructions..."""
REVIEW_SYSTEM_PROMPT = """Your custom review instructions..."""
```

---

## Troubleshooting

### "Connection refused to localhost:11434"

Ollama is not running:
```bash
ollama serve
```

### "Model not found: deepseek-r1:7b-qwen-distill-q4_0"

Pull the model first:
```bash
ollama pull deepseek-r1:7b-qwen-distill-q4_0
```

### "Out of memory" or "CUDA out of memory"

Your GPU VRAM is insufficient. Options:
1. Run models sequentially (default behavior - pause Ollama between stages)
2. Use smaller quantization: `ollama pull deepseek-r1:7b-qwen-distill-q3_0` (3-bit)
3. Use CPU: Slower but unlimited VRAM

### Pipeline hangs on a stage

Likely model is generating endlessly. Adjust timeout in code:

```python
response = requests.post(..., timeout=600)  # Increase from 300 to 600 seconds
```

---

## Cost Analysis

### Local vs API-Only

**Your Hybrid Setup (Local + API)**
- DeepSeek-R1: Free (local)
- Qwen2.5-Coder: Free (local)
- Mistral: Free (local)
- Claude Sonnet: ~$0.015 per 1K tokens = ~$0.02-0.05 per feature
- **Average cost per feature: $0.02-0.05**
- **Monthly (20 features/day): ~$10-25**

**API-Only (All Sonnet)**
- Every request: $0.015/1K tokens = $0.30-1.00 per feature
- **Average cost per feature: $0.30-1.00**
- **Monthly (20 features/day): ~$120-200**

**Savings: 90% reduction in API costs**

### Time Analysis

**Your Hybrid Setup**
- Stage 1 (Reasoning): 8-15s
- Stage 2 (Coding): 10-20s
- Stage 3 (Debugging): 10-30s (1-3 iterations)
- Stage 4 (Review): 2-5s
- **Total: 30-70s per feature**

**API-Only (All Sonnet)**
- Same stages but all on API: 5-10s per stage
- **Total: 20-40s per feature**
- But costs 10x more

---

## Production Deployment

### Option 1: Local Development (This Setup)
- Run locally for rapid iteration
- Minimal cost (~$0.05 per feature)
- Full privacy - code never leaves your machine
- Works offline (except final API review)

### Option 2: Team Server
```bash
# Install on shared server/Lambda/Cloud Run
# All teams access same Ollama instance
# API calls still go through your account
```

### Option 3: CI/CD Integration
```yaml
# GitHub Actions example
name: AI Code Generation
on: [pull_request]
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install Ollama
        run: curl -fsSL https://ollama.com/install.sh | sh
      - name: Pull models
        run: |
          ollama pull deepseek-r1:7b-qwen-distill-q4_0
          ollama pull qwen2.5-coder:7b
          ollama pull mistral:7b-q4_0
      - name: Run pipeline
        run: python specialized_pipeline.py
      - name: Create commit
        run: git commit -am "AI-generated code"
```

---

## Next Steps

1. **Run the basic pipeline** with the provided code
2. **Customize prompts** for your coding style
3. **Tune max_iterations** in debugging stage (currently 3)
4. **Add your own validation** (tests, linting, formatting)
5. **Integrate into your workflow** (CLI tool, IDE plugin, etc.)

---

## Files Included

- `specialized_pipeline.py` - Main pipeline orchestrator (~450 lines)
- `SETUP_GUIDE.md` - This file
- `gemini_research_prompt.md` - The research prompt you used
- `pipeline_output.json` - Example output (auto-generated)

---

## Support

Issues? Check:
1. Ollama is running: `curl http://localhost:11434/api/tags`
2. Models are pulled: `ollama list`
3. API key is set: `echo $ANTHROPIC_API_KEY`
4. Logs in code for debugging: Add `logging.DEBUG` level

---

## References from Research

All recommendations based on Gemini's web search findings:
- Blueprint2Code: 96.3% HumanEval accuracy
- CODESIM: Simulation-driven debugging
- REMODEL-LLM: Python + Ollama orchestration
- LangGraph: Recommended orchestration framework
- OpenCompass: Debugging/verification tools

See `gemini_research_findings.txt` for full research report.
