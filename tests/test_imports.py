import os

def test_pipeline_import():
    """Basic test to verify pipeline components are importable."""
    try:
        import specialized_pipeline
        import doggy_ai
        print("Pipeline components imported successfully.")
    except ImportError as e:
        print(f"Failed to import components: {e}")
        assert False

if __name__ == "__main__":
    test_pipeline_import()
