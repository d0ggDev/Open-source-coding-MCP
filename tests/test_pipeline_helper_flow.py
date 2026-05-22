from specialized_pipeline import run_pipeline, PromptConfig

# Define custom prompts to ensure high-quality, documented output
config = PromptConfig(
    reasoning="You are a senior software architect. Create a detailed design document in JSON with 'problem_analysis', 'architecture_pattern', and 'acceptance_criteria'.",
    coding="You are a senior developer. Write clean, PEP8-compliant Python code with comprehensive docstrings and type hints.",
    debugging="You are an expert QA engineer. Focus on finding race conditions and input validation issues.",
    review="You are a Principal Engineer. Perform a rigorous, detailed review of the code's architecture and performance."
)

# Run the pipeline
requirement = "Build a simple CLI task timer that allows users to start and stop a timer for specific tasks."
result = run_pipeline(requirement, prompt_config=config)

print("\nPipeline execution complete.")
print(f"Revisions: {result['revision_count']}")
print(f"Review outcome: {result['final_code'][:100]}...")
