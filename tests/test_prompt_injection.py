from specialized_pipeline import run_pipeline, PromptConfig

# Custom prompt to force a specific style for the design document
custom_reasoning_prompt = """You are a minimalist software architect. 
Provide the design document in JSON, using ONLY the following fields:
- summary
- tech_stack

Output ONLY valid JSON."""

# Create the config
config = PromptConfig(reasoning=custom_reasoning_prompt)

# Execute the pipeline with the custom config
# Note: Since the real pipeline runs all stages, we'll see if the design stage uses our custom prompt
requirement = "Build a simple web crawler"
result = run_pipeline(requirement, prompt_config=config)

# Verify the design output
print("\n--- DESIGN OUTPUT ---")
print(result['design'])

# Check if the design contains the fields we requested
if '"summary"' in result['design'] and '"tech_stack"' in result['design'] and '"problem_analysis"' not in result['design']:
    print("\n✅ Success: Custom prompt was honored!")
else:
    print("\n❌ Failure: Custom prompt was not honored.")
