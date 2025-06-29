#!/usr/bin/env python3
"""
Diff Generator Agent - Automatically generates diff.json for code review
Supports various git scenarios: branch comparison, commit comparison, staged changes, etc.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DiffGeneratorAgent:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        if not self.is_git_repo():
            raise ValueError(f"Not a git repository: {self.repo_path}")
    
    def is_git_repo(self) -> bool:
        """Check if the given path is a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_diff(self, base: str, target: str = "HEAD") -> Dict[str, str]:
        """
        Get diff between two git references.
        
        Args:
            base: Base reference (branch, commit, etc.)
            target: Target reference (default: HEAD)
        
        Returns:
            Dictionary mapping file paths to their unified diff strings
        """
        try:
            # Get list of changed files
            files_cmd = ["git", "diff", "--name-only", f"{base}..{target}"]
            result = subprocess.run(
                files_cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = result.stdout.strip().split('\n')
            changed_files = [f for f in changed_files if f]  # Remove empty lines
            
            if not changed_files:
                print(f"No changes found between {base} and {target}")
                return {}
            
            # Get diff for each file
            diffs = {}
            for file_path in changed_files:
                diff_cmd = ["git", "diff", f"{base}..{target}", "--", file_path]
                result = subprocess.run(
                    diff_cmd,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                diffs[file_path] = result.stdout
            
            return diffs
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting diff: {e}")
            print(f"stderr: {e.stderr}")
            return {}
    
    def get_staged_diff(self) -> Dict[str, str]:
        """Get diff for staged changes."""
        try:
            # Get list of staged files
            files_cmd = ["git", "diff", "--cached", "--name-only"]
            result = subprocess.run(
                files_cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            staged_files = result.stdout.strip().split('\n')
            staged_files = [f for f in staged_files if f]
            
            if not staged_files:
                print("No staged changes found")
                return {}
            
            # Get diff for each staged file
            diffs = {}
            for file_path in staged_files:
                diff_cmd = ["git", "diff", "--cached", "--", file_path]
                result = subprocess.run(
                    diff_cmd,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                diffs[file_path] = result.stdout
            
            return diffs
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting staged diff: {e}")
            return {}
    
    def get_unstaged_diff(self) -> Dict[str, str]:
        """Get diff for unstaged changes."""
        try:
            # Get list of unstaged files
            files_cmd = ["git", "diff", "--name-only"]
            result = subprocess.run(
                files_cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            unstaged_files = result.stdout.strip().split('\n')
            unstaged_files = [f for f in unstaged_files if f]
            
            if not unstaged_files:
                print("No unstaged changes found")
                return {}
            
            # Get diff for each unstaged file
            diffs = {}
            for file_path in unstaged_files:
                diff_cmd = ["git", "diff", "--", file_path]
                result = subprocess.run(
                    diff_cmd,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                diffs[file_path] = result.stdout
            
            return diffs
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting unstaged diff: {e}")
            return {}
    
    def get_commit_diff(self, commit_hash: str) -> Dict[str, str]:
        """Get diff for a specific commit."""
        try:
            # Get list of files changed in the commit
            files_cmd = ["git", "show", "--name-only", "--pretty=format:", commit_hash]
            result = subprocess.run(
                files_cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = result.stdout.strip().split('\n')
            changed_files = [f for f in changed_files if f]
            
            if not changed_files:
                print(f"No changes found in commit {commit_hash}")
                return {}
            
            # Get diff for the commit
            diff_cmd = ["git", "show", commit_hash]
            result = subprocess.run(
                diff_cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the diff to separate files
            diff_output = result.stdout
            diffs = self._parse_commit_diff(diff_output)
            
            return diffs
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting commit diff: {e}")
            return {}
    
    def _parse_commit_diff(self, diff_output: str) -> Dict[str, str]:
        """Parse commit diff output to separate files."""
        diffs = {}
        current_file = None
        current_diff = []
        
        for line in diff_output.split('\n'):
            if line.startswith('diff --git'):
                # Save previous file diff
                if current_file and current_diff:
                    diffs[current_file] = '\n'.join(current_diff)
                
                # Start new file
                parts = line.split()
                if len(parts) >= 3:
                    current_file = parts[2].replace('b/', '')
                    current_diff = [line]
                else:
                    current_file = None
                    current_diff = []
            elif current_file:
                current_diff.append(line)
        
        # Save last file diff
        if current_file and current_diff:
            diffs[current_file] = '\n'.join(current_diff)
        
        return diffs
    
    def generate_diff_json(self, output_file: str = "diff.json", **kwargs) -> bool:
        """
        Generate diff.json file based on the provided parameters.
        
        Args:
            output_file: Output JSON file path
            **kwargs: Diff parameters (base, target, mode, etc.)
        
        Returns:
            True if successful, False otherwise
        """
        diffs = {}
        
        if kwargs.get('mode') == 'staged':
            diffs = self.get_staged_diff()
        elif kwargs.get('mode') == 'unstaged':
            diffs = self.get_unstaged_diff()
        elif kwargs.get('mode') == 'commit':
            commit_hash = kwargs.get('commit_hash')
            if not commit_hash:
                print("Error: commit_hash required for commit mode")
                return False
            diffs = self.get_commit_diff(commit_hash)
        else:
            # Default: branch comparison
            base = kwargs.get('base', 'main')
            target = kwargs.get('target', 'HEAD')
            diffs = self.get_diff(base, target)
        
        if not diffs:
            print("No changes found to generate diff.json")
            return False
        
        # Create the JSON structure
        diff_data = {"files": diffs}
        
        # Write to file
        try:
            with open(output_file, 'w') as f:
                json.dump(diff_data, f, indent=2)
            print(f"Generated {output_file} with {len(diffs)} files")
            return True
        except Exception as e:
            print(f"Error writing {output_file}: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate diff.json for code review from git repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare current branch with main
  python diff_generator_agent.py --base main --target HEAD
  
  # Generate diff for staged changes
  python diff_generator_agent.py --mode staged
  
  # Generate diff for specific commit
  python diff_generator_agent.py --mode commit --commit-hash abc123
  
  # Compare two branches
  python diff_generator_agent.py --base feature-branch --target main
        """
    )
    
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
    
    args = parser.parse_args()
    
    try:
        agent = DiffGeneratorAgent(args.repo_path)
        
        kwargs = {
            'mode': args.mode,
            'base': args.base,
            'target': args.target,
            'commit_hash': args.commit_hash
        }
        
        success = agent.generate_diff_json(args.output, **kwargs)
        if success:
            print(f"Successfully generated {args.output}")
            sys.exit(0)
        else:
            print("Failed to generate diff.json")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 