import requests
import json
import sys

def stream_llm_response(model, prompt):
    url = 'http://localhost:11434/api/generate'
    payload = {
        'model': model,
        'prompt': prompt,
        'stream': True,
        'temperature': 0.3
    }
    
    full_response = ""
    print(f"\n--- Model: {model} ---")
    
    with requests.post(url, json=payload, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if 'done' in chunk and chunk['done']:
                    break
                
                # Ollama returns 'response' for generation models
                if 'response' in chunk:
                    content = chunk['response']
                    print(content, end="", flush=True)
                    full_response += content
                    
    print("\n---------------------------")
    return full_response

if __name__ == "__main__":
    # Test reasoning
    stream_llm_response('deepseek-r1:8b', 'Explain quantum computing in one sentence.')
