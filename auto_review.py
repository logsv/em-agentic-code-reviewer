#!/usr/bin/env python3
"""
Auto Review - Combined script that generates diff.json and runs code review automatically
Provides a seamless workflow for code review automation.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from diff_generator_agent import DiffGeneratorAgent
from llm_providers.factory import LLMProviderFactory


def run_code_review(diff_file: str, provider: str, model: str = None, **kwargs):
    """Run the code review agent with the generated diff file."""
    cmd = ["python", "eng_manager_review_agent.py", diff_file, provider]
    if model:
        cmd.append(model)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("=== CODE REVIEW RESULTS ===")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running code review: {e}")
        print(f"stderr: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Automatically generate diff and run code review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Review current branch vs main using OpenAI
  python auto_review.py --provider openai --model gpt-4
  
  # Review staged changes using local deepseek-r1
  python auto_review.py --mode staged --provider local --model deepseek-r1
  
  # Review specific commit using Claude
  python auto_review.py --mode commit --commit-hash abc123 --provider claude
  
  # Review branch comparison with custom output
  python auto_review.py --base feature-branch --target main --provider openai --output my_review.json
        """
    )
    
    # Diff generation arguments
    parser.add_argument(
        '--repo-path', 
        default='.', 
        help='Path to git repository (default: current directory)'
    )
    parser.add_argument(
        '--output', 
        default='diff.json', 
        help='Output JSON file (default: diff.json)'
    )
    parser.add_argument(
        '--mode',
        choices=['branch', 'staged', 'unstaged', 'commit'],
        default='branch',
        help='Diff mode (default: branch)'
    )
    parser.add_argument(
        '--base',
        default='main',
        help='Base reference for branch comparison (default: main)'
    )
    parser.add_argument(
        '--target',
        default='HEAD',
        help='Target reference for branch comparison (default: HEAD)'
    )
    parser.add_argument(
        '--commit-hash',
        help='Commit hash for commit mode'
    )
    
    # Code review arguments
    parser.add_argument(
        '--provider',
        choices=LLMProviderFactory.get_supported_providers(),
        required=True,
        help='LLM provider for code review'
    )
    parser.add_argument(
        '--model',
        help='Model name (e.g., gpt-4, gemini-pro, deepseek-r1)'
    )
    parser.add_argument(
        '--skip-diff-generation',
        action='store_true',
        help='Skip diff generation and use existing diff.json file'
    )
    parser.add_argument(
        '--skip-review',
        action='store_true',
        help='Only generate diff.json, skip code review'
    )
    parser.add_argument(
        '--list-providers',
        action='store_true',
        help='List all supported providers and models'
    )
    
    args = parser.parse_args()
    
    # List providers if requested
    if args.list_providers:
        print("Supported LLM Providers:")
        print("=" * 50)
        for name, info in LLMProviderFactory.get_provider_info().items():
            print(f"\n{name.upper()}:")
            print(f"  Default Model: {info['default_model']}")
            print(f"  Supported Models: {', '.join(info['models'])}")
        return
    
    try:
        # Step 1: Generate diff.json (unless skipped)
        if not args.skip_diff_generation:
            print("=== GENERATING DIFF ===")
            agent = DiffGeneratorAgent(args.repo_path)
            
            kwargs = {
                'mode': args.mode,
                'base': args.base,
                'target': args.target,
                'commit_hash': args.commit_hash
            }
            
            success = agent.generate_diff_json(args.output, **kwargs)
            if not success:
                print("Failed to generate diff.json")
                sys.exit(1)
        else:
            if not os.path.exists(args.output):
                print(f"Error: {args.output} not found. Use --skip-diff-generation only if the file exists.")
                sys.exit(1)
            print(f"Using existing {args.output}")
        
        # Step 2: Run code review (unless skipped)
        if not args.skip_review:
            print("\n=== RUNNING CODE REVIEW ===")
            success = run_code_review(args.output, args.provider, args.model)
            if not success:
                print("Code review failed")
                sys.exit(1)
        else:
            print(f"Diff generated successfully: {args.output}")
            print("Skipping code review as requested")
        
        print("\n=== COMPLETED ===")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 