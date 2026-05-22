"""
Specialized Model Code Generation Pipeline
Reasoning (DeepSeek-R1) → Coding (Qwen2.5-Coder) → Debugging (Verification) → Review (Gemini/Claude API)

This orchestrates the exact architecture from Gemini's research findings.
"""

import json
import re
import subprocess
from typing import TypedDict, Annotated, Optional
from datetime import datetime
import logging

from langgraph.graph import StateGraph, END
from anthropic import Anthropic
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# STATE DEFINITION
# ============================================================================

class PromptConfig:
    """Configurable system prompts for each pipeline stage."""
    def __init__(self, reasoning=None, coding=None, debugging=None, review=None):
        self.reasoning = reasoning or REASONING_SYSTEM_PROMPT
        self.coding = coding or CODING_SYSTEM_PROMPT
        self.debugging = debugging or DEBUG_SYSTEM_PROMPT
        self.review = review or REVIEW_SYSTEM_PROMPT

class PipelineState(TypedDict):
    """Central state machine for the entire pipeline"""
    requirement: str
    design: str
    code: str
    code_files: dict
    debug_results: str
    issues_found: list
    revision_count: int
    final_code: str
    metadata: dict
    prompt_config: PromptConfig  # Added prompt configuration



# ============================================================================
# STAGE 1: REASONING (DeepSeek-R1-Distill-Qwen)
# ============================================================================

REASONING_SYSTEM_PROMPT = """You are a software architect. Create a design document in JSON.

FIELDS REQUIRED:
- problem_analysis
- architecture_pattern
- data_model
- implementation_strategy
- edge_cases
- acceptance_criteria

Output ONLY valid JSON."""


def reasoning_stage(state: PipelineState) -> PipelineState:
    """Stage 1: DeepSeek-R1 generates architecture/design with streaming"""
    logger.info("Stage 1: Reasoning (DeepSeek-R1)...")
    
    prompt = f"""{state['prompt_config'].reasoning}

REQUIREMENT:
{state['requirement']}

Output JSON design document:"""
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'deepseek-r1:8b',
                'prompt': prompt,
                'stream': True,
                'temperature': 0.7,
            },
            timeout=300,
            stream=True
        )
        response.raise_for_status()
        
        design_text = ""
        print("\n[Thinking/Design]: ", end="", flush=True)
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if 'response' in chunk:
                    content = chunk['response']
                    print(content, end="", flush=True)
                    design_text += content
        print("\n")
        
        # Extract JSON from response
        try:
            json_match = re.search(r'\{.*\}', design_text, re.DOTALL)
            if json_match:
                state['design'] = json_match.group()
            else:
                state['design'] = design_text
        except:
            state['design'] = design_text
            
        logger.info("✓ Design generated")
        return state
        
    except Exception as e:
        logger.error(f"Reasoning stage failed: {e}")
        raise


# ============================================================================
# STAGE 2: CODING (Qwen2.5-Coder)
# ============================================================================

CODING_SYSTEM_PROMPT = """You are an expert developer. Implement the design exactly as specified.

RULES:
1. Follow design architecture exactly
2. Include error handling and docstrings
3. Write production-ready, typed code.
4. Add unit tests.
5. Generate clean, complete, concise code.

OUTPUT FORMAT:
Generate your response as a JSON object with a list of files:
{
  "files": [
    {
      "filename": "path/to/file.ext",
      "purpose": "1-line description",
      "content": "Full source code here"
    }
  ]
}"""


def coding_stage(state: PipelineState) -> PipelineState:
    """Stage 2: Qwen2.5-Coder generates code using JSON tool format"""
    logger.info("Stage 2: Coding (Qwen2.5-Coder)...")
    
    # Escape curly braces for format()
    prompt = state['prompt_config'].coding.replace('{', '{{').replace('}', '}}').format(design=state['design']) + f"""

NOW IMPLEMENT:
{state['requirement']}

Write complete, production-ready code in the requested JSON format:"""
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'qwen2.5-coder:7b',
                'prompt': prompt,
                'stream': False,
                'temperature': 0.1,
            },
            timeout=300
        )
        response.raise_for_status()
        
        # Parse JSON
        result_json = response.json()['response']
        match = re.search(r'\{.*\}', result_json, re.DOTALL)
        if match:
            data = json.loads(match.group())
            state['code_files'] = {f['filename']: f for f in data['files']}
            state['code'] = "\n".join([f['content'] for f in data['files']])
        else:
            # Fallback if no JSON found
            logger.error("Failed to parse code files JSON")
            state['code_files'] = {}
            state['code'] = result_json
            
        logger.info(f"✓ Code generated ({len(state['code_files'])} files)")
        return state
        
    except Exception as e:
        logger.error(f"Coding stage failed: {e}")
        raise


# ============================================================================
# STAGE 3: DEBUGGING (Local verification loop)
# ============================================================================

DEBUG_SYSTEM_PROMPT = """You are a senior engineer. Review the provided code against the design and find bugs.

CODE:
{code}

DESIGN:
{design}

OUTPUT JSON:
{{
  "issues": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "type": "logic|security|edge-case",
      "location": "file:line",
      "problem": "description",
      "fix": "fix instruction"
    }}
  ],
  "summary": "Brief assessment"
}}

Output ONLY valid JSON."""


def debugging_stage(state: PipelineState, max_iterations: int = 3) -> PipelineState:
    """Stage 3: Verify code, loop up to max_iterations to fix issues"""
    logger.info(f"Stage 3: Debugging (max {max_iterations} iterations)...")
    
    for iteration in range(max_iterations):
        logger.info(f"  Iteration {iteration + 1}/{max_iterations}...")
        
        prompt = state['prompt_config'].debugging.format(
            code=state['code'],
            design=state['design']
        )
        
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'gemma3:4b',
                    'prompt': prompt,
                    'stream': False,
                    'temperature': 0.3,
                },
                timeout=300
            )

            response.raise_for_status()
            debug_output = response.json()['response']
            state['debug_results'] = debug_output
            
            # Parse issues
            try:
                json_match = re.search(r'\{.*\}', debug_output, re.DOTALL)
                if json_match:
                    issues = json.loads(json_match.group())['issues']
                    state['issues_found'] = issues
                else:
                    state['issues_found'] = []
            except:
                state['issues_found'] = []
            
            # Check if there are HIGH severity issues
            high_severity = [i for i in state['issues_found'] if i.get('severity') == 'HIGH']
            
            if not high_severity:
                logger.info(f"  ✓ No high-severity issues found")
                break
            
            logger.info(f"  Found {len(high_severity)} high-severity issues, revising...")
            
            # Revise code
            revision_prompt = f"""Original code:
{state['code']}

Issues found:
{json.dumps(high_severity, indent=2)}

Fix these issues while preserving the design:"""
            
            revision_response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'qwen2.5-coder:7b',
                    'prompt': revision_prompt,
                    'stream': False,
                    'temperature': 0.3,
                },
                timeout=300
            )
            revision_response.raise_for_status()
            state['code'] = revision_response.json()['response']
            state['code_files'] = parse_code_files(state['code'])
            state['revision_count'] += 1
            
        except Exception as e:
            logger.error(f"Debugging iteration {iteration + 1} failed: {e}")
            if iteration == max_iterations - 1:
                raise
    
    logger.info("✓ Debugging complete")
    return state


# ============================================================================
# STAGE 4: REVIEW (Gemini/Claude API - Final validation)
# ============================================================================

REVIEW_SYSTEM_PROMPT = """You are a principal engineer doing final code review.

This code has been through reasoning, implementation, and local debugging.

DESIGN:
{design}

CODE:
{code}

LOCAL ISSUES FOUND AND FIXED:
{debug_issues}

Do a final sweep for:
1. Does this solve the original requirement?
2. Are there logical flaws the local models missed?
3. Performance optimizations?
4. Architectural improvements?
5. Is it production-ready?

If APPROVED: Start response with "APPROVED:" and provide any final tweaks.
If NEEDS_WORK: Start response with "NEEDS_WORK:" and list specific items.

Be concise. This is the final gate before production."""


def review_stage(state: PipelineState) -> PipelineState:
    """Stage 4: Review stage with local fallback"""
    logger.info("Stage 4: Review (Claude API with local fallback)...")
    
    review_prompt = REVIEW_SYSTEM_PROMPT.format(
        design=state['design'],
        code=state['code'],
        debug_issues=json.dumps(state['issues_found'], indent=2)
    )
    
    try:
        from anthropic import Anthropic
        client = Anthropic()
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=500,
            messages=[{"role": "user", "content": review_prompt}]
        )
        review_text = response.content[0].text
    except Exception as e:
        logger.warning(f"API Review failed, falling back to local review: {e}")
        # Local fallback using qwen2.5-coder
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'qwen2.5-coder:7b',
                'prompt': review_prompt,
                'stream': False,
                'temperature': 0.2,
            },
            timeout=300
        )
        response.raise_for_status()
        review_text = response.json()['response']

    state['final_code'] = review_text
    
    if "APPROVED" in review_text:
        logger.info("✓ APPROVED by reviewer")
    else:
        logger.info("⚠ Needs revision based on reviewer feedback")
    
    return state


# ============================================================================
# ROUTING LOGIC
# ============================================================================

def route_to_review_or_revise(state: PipelineState) -> str:
    """Decide: if high-severity issues remain, revise. Otherwise, proceed to review."""
    high_severity = [i for i in state['issues_found'] if i.get('severity') == 'HIGH']
    
    if high_severity and state['revision_count'] < 3:
        return "revise"
    return "review"


# ============================================================================
# BUILD THE GRAPH
# ============================================================================
from langgraph.graph import StateGraph, END, START
...
def build_pipeline() -> StateGraph:
    """Construct the LangGraph state machine"""

    graph = StateGraph(PipelineState)

    # Add nodes
    graph.add_node("reasoning", reasoning_stage)
    graph.add_node("coding", coding_stage)
    graph.add_node("debugging", debugging_stage)
    graph.add_node("review", review_stage)

    # Add edges
    graph.add_edge(START, "reasoning")
    graph.add_edge("reasoning", "coding")
    graph.add_edge("coding", "debugging")
    graph.add_edge("debugging", "review")
    graph.add_edge("review", END)

    return graph.compile()


# ============================================================================
# EXECUTION
# ============================================================================

def run_pipeline(requirement: str, prompt_config: PromptConfig = None) -> dict:
    """Execute the full pipeline"""
    
    logger.info("=" * 80)
    logger.info("SPECIALIZED MODEL CODE GENERATION PIPELINE")
    logger.info("=" * 80)
    logger.info(f"Requirement: {requirement}\n")
    
    if prompt_config is None:
        prompt_config = PromptConfig()
    
    pipeline = build_pipeline()
    
    initial_state = PipelineState(
        requirement=requirement,
        design="",
        code="",
        code_files={},
        debug_results="",
        issues_found=[],
        revision_count=0,
        final_code="",
        metadata={
            'started_at': datetime.now().isoformat(),
            'models_used': {
                'reasoning': 'deepseek-r1:8b',
                'coding': 'qwen2.5-coder:3b',
                'debugging': 'gemma3:4b',
                'review': 'claude-opus-4-6'
            }
        },
        prompt_config=prompt_config
    )
    
    try:
        result = pipeline.invoke(initial_state)
        
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Revisions needed: {result['revision_count']}")
        logger.info(f"Files generated: {len(result['code_files'])}")
        logger.info(f"Final review: {result['final_code'][:100]}...")
        
        return result
        
    except Exception as e:
        logger.error(f"\nPipeline failed at some stage: {e}")
        raise


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    requirement = """Build a REST API for user authentication that:
    - Supports signup/login/logout with JWT tokens
    - Password reset via email verification
    - Rate limiting (5 attempts/hour per IP)
    - Input validation and OWASP compliance
    - PostgreSQL storage with bcrypt hashing
    """
    
    result = run_pipeline(requirement)
    
    # Save output
    with open("pipeline_output.json", "w") as f:
        json.dump({
            'requirement': result['requirement'],
            'design': result['design'],
            'files': result['code_files'],
            'debug_issues': result['issues_found'],
            'review': result['final_code'],
            'metadata': result['metadata']
        }, f, indent=2)
    
    # Save individual files
    for filename, data in result['code_files'].items():
        try:
            with open(filename, "w") as f:
                f.write(data['content'])
            print(f"✓ Saved {filename}")
        except Exception as e:
            print(f"✗ Failed to save {filename}: {e}")
    
    print("\n✓ Output saved to pipeline_output.json")
