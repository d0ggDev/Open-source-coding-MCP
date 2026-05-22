#!/usr/bin/env python3
"""
doggy-ai: CLI for specialized model code generation pipeline

Usage:
  doggy-ai build "Build a REST API for user auth"
  doggy-ai design "System design for real-time chat"
  doggy-ai debug "path/to/file.ts"
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import logging

from specialized_pipeline import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_build(args):
    """Build complete feature: reasoning → coding → debugging → review"""
    requirement = args.requirement
    
    logger.info(f"\n🚀 Building: {requirement}\n")
    
    result = run_pipeline(requirement)
    
    # Save output
    output_file = f"doggy_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'requirement': result['requirement'],
            'design': result['design'],
            'code': result['code'],
            'files': result['code_files'],
            'issues_found': result['issues_found'],
            'revisions': result['revision_count'],
            'review': result['final_code'],
        }, f, indent=2)
    
    logger.info(f"\n✅ Complete! Output saved to: {output_file}\n")
    
    # Display summary
    print("\n" + "="*80)
    print("PIPELINE SUMMARY")
    print("="*80)
    print(f"Files generated: {len(result['code_files'])}")
    print(f"Debugging iterations: {result['revision_count']}")
    print(f"Issues found: {len(result['issues_found'])}")
    print("\nFiles:")
    for filename in result['code_files']:
        print(f"  - {filename}")
    print("\n" + "="*80)


def cmd_design(args):
    """Just run reasoning stage to get design"""
    requirement = args.requirement
    
    logger.info(f"\n📐 Generating design: {requirement}\n")
    
    from specialized_pipeline import reasoning_stage, PipelineState
    
    state = PipelineState(
        requirement=requirement,
        design="",
        code="",
        code_files={},
        debug_results="",
        issues_found=[],
        revision_count=0,
        final_code="",
        metadata={}
    )
    
    result = reasoning_stage(state)
    
    output_file = f"design_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'requirement': requirement,
            'design': result['design']
        }, f, indent=2)
    
    logger.info(f"\n✅ Design generated! Saved to: {output_file}\n")
    
    print("\nDESIGN:")
    print("="*80)
    print(result['design'])
    print("="*80)


def cmd_debug(args):
    """Run debugging stage on existing code"""
    filepath = args.file
    
    if not Path(filepath).exists():
        logger.error(f"File not found: {filepath}")
        sys.exit(1)
    
    with open(filepath, 'r') as f:
        code = f.read()
    
    logger.info(f"\n🐛 Debugging: {filepath}\n")
    
    from specialized_pipeline import debugging_stage, PipelineState
    
    state = PipelineState(
        requirement="Debug existing code",
        design="",
        code=code,
        code_files={},
        debug_results="",
        issues_found=[],
        revision_count=0,
        final_code="",
        metadata={}
    )
    
    result = debugging_stage(state, max_iterations=3)
    
    output_file = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'file': filepath,
            'issues': result['issues_found'],
            'debug_output': result['debug_results']
        }, f, indent=2)
    
    logger.info(f"\n✅ Debug complete! Issues saved to: {output_file}\n")
    
    if result['issues_found']:
        print("\nISSUES FOUND:")
        print("="*80)
        for issue in result['issues_found']:
            severity = issue.get('severity', 'UNKNOWN')
            issue_type = issue.get('type', 'unknown')
            print(f"\n[{severity}] {issue_type}")
            print(f"  Location: {issue.get('location', 'N/A')}")
            print(f"  Problem: {issue.get('problem', 'N/A')}")
            print(f"  Fix: {issue.get('fix', 'N/A')}")
        print("\n" + "="*80)
    else:
        print("\n✅ No issues found!\n")


def cmd_review(args):
    """Just run review stage on code"""
    filepath = args.file
    
    if not Path(filepath).exists():
        logger.error(f"File not found: {filepath}")
        sys.exit(1)
    
    with open(filepath, 'r') as f:
        code = f.read()
    
    logger.info(f"\n📋 Reviewing: {filepath}\n")
    
    from specialized_pipeline import review_stage, PipelineState
    
    state = PipelineState(
        requirement="Review existing code",
        design="",
        code=code,
        code_files={},
        debug_results="",
        issues_found=[],
        revision_count=0,
        final_code="",
        metadata={}
    )
    
    result = review_stage(state)
    
    print("\nREVIEW:")
    print("="*80)
    print(result['final_code'])
    print("="*80)


def cmd_status(args):
    """Check if pipeline dependencies are ready"""
    import subprocess
    
    print("\nChecking dependencies...\n")
    
    checks = []
    
    # Check Ollama
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://localhost:11434/api/tags'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Ollama is running")
            checks.append(True)
        else:
            print("❌ Ollama is not responding")
            checks.append(False)
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        checks.append(False)
    
    # Check Anthropic API key
    try:
        import os
        if os.getenv('ANTHROPIC_API_KEY'):
            print("✅ Anthropic API key is set")
            checks.append(True)
        else:
            print("❌ Anthropic API key not found")
            checks.append(False)
    except Exception as e:
        print(f"❌ API key check failed: {e}")
        checks.append(False)
    
    # Check models
    try:
        import subprocess
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        models = {
            'deepseek-r1': False,
            'qwen2.5-coder': False,
            'mistral': False,
        }
        
        for model_name in models:
            if model_name in result.stdout:
                models[model_name] = True
        
        for model, found in models.items():
            status = "✅" if found else "❌"
            print(f"{status} {model}: {'installed' if found else 'not found'}")
            checks.append(found)
    
    except Exception as e:
        print(f"❌ Model check failed: {e}")
        checks.append(False)
    
    print("\n" + "="*80)
    if all(checks):
        print("✅ All systems ready!")
    else:
        print("⚠️  Some dependencies missing. See SETUP_GUIDE.md")
    print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='doggy-ai: Specialized model code generation pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  doggy-ai build "Build REST API for user authentication"
  doggy-ai design "System design for real-time chat"
  doggy-ai debug src/app.ts
  doggy-ai review src/app.ts
  doggy-ai status
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # build command
    build_parser = subparsers.add_parser('build', help='Full pipeline: reasoning→coding→debug→review')
    build_parser.add_argument('requirement', help='Feature requirement description')
    build_parser.set_defaults(func=cmd_build)
    
    # design command
    design_parser = subparsers.add_parser('design', help='Just reasoning stage')
    design_parser.add_argument('requirement', help='Requirement to design')
    design_parser.set_defaults(func=cmd_design)
    
    # debug command
    debug_parser = subparsers.add_parser('debug', help='Debug existing code')
    debug_parser.add_argument('file', help='Path to code file')
    debug_parser.set_defaults(func=cmd_debug)
    
    # review command
    review_parser = subparsers.add_parser('review', help='Review existing code')
    review_parser.add_argument('file', help='Path to code file')
    review_parser.set_defaults(func=cmd_review)
    
    # status command
    status_parser = subparsers.add_parser('status', help='Check pipeline status')
    status_parser.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
