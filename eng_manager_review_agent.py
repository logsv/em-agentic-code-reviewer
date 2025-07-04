import os
import json
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from llm_providers.factory import LLMProviderFactory
from diff_generator_agent import DiffGeneratorAgent
from tools import run_flake8, run_bandit, run_snyk, run_mypy, run_pylint, run_eslint, run_npm_audit, run_golint, run_gosec, run_govulncheck, TOOLS
from repo_utils import detect_repo_types, get_tools_for_repo_types

# Optional: import LLM SDKs
try:
    import openai
except ImportError:
    openai = None
try:
    import google.generativeai as genai
except ImportError:
    genai = None
try:
    import ollama
except ImportError:
    ollama = None

# Tool functions
import subprocess

def run_flake8(repo_path):
    result = subprocess.run([
        "flake8", repo_path
    ], capture_output=True, text=True)
    return result.stdout

def run_bandit(repo_path):
    result = subprocess.run([
        "bandit", "-r", repo_path, "-f", "json"
    ], capture_output=True, text=True)
    return result.stdout

def run_snyk(repo_path):
    result = subprocess.run([
        "snyk", "test", repo_path, "--json"
    ], capture_output=True, text=True)
    return result.stdout

TOOLS = {
    "flake8": run_flake8,
    "bandit": run_bandit,
    "snyk": run_snyk,
}

TEAM_GUIDING_PRINCIPLES = [
    "Code readability & overall architecture clarity",
    "Scalability, performance, and operational considerations",
    "Security and compliance risk surface",
    "Developer experience (test coverage, documentation, ease of change)",
    "Alignment with product goals and roadmap",
]

REVIEW_POINTS = [
    ("Design & Architecture", [
        "Does the change fit our modular boundaries?",
        "Are abstractions clear or is there hidden coupling?",
        "Will this pattern scale as the codebase grows?",
        "Are responsibilities extracted into small, focused, and manageable functions?",
        "Are there clear interfaces and public methods?",
        "Is there any tight coupling or unclear boundaries that could make the code fragile?",
    ]),
    ("Maintainability & Team Impact", [
        "Is test coverage sufficient for this change?",
        "Are public APIs or interfaces changing—what's the migration plan?",
        "Will this increase the cognitive load on future maintainers?",
        "Is the code organized and easy to navigate?",
        "Are there large functions or 'god classes' that should be refactored?",
        "Is there any copy-pasted or duplicate code that should be shared as utilities?",
    ]),
    ("Performance & Operational Risk", [
        "Highlight any potential hot spots or misuse of resources.",
        "Call out external dependencies, feature flags, rollout strategies.",
    ]),
    ("Security & Compliance", [
        "Surface any new risks (injection, data leaks, auth bypass).",
        "Confirm that secrets handling, logging, and audit hooks are in place.",
        "Is all input validated and sanitized?",
        "Are proven libraries used for authentication and encryption?",
        "Is there any custom authentication or skipped security checks?",
    ]),
    ("Documentation & Release Readiness", [
        "Ensure README, docs, and CHANGELOG are updated.",
        "Note any release-day or config steps required.",
    ]),
    ("Code Quality & Standards", [
        "Is the code style consistent with the team's standards?",
        "Are formatters and linters enforced?",
        "Is there any evidence of lax coding standards or inconsistent style?",
    ]),
    ("Testing", [
        "Are there sufficient tests for new features or bug fixes?",
        "Is there any untested code or lack of a testing framework?",
        "Are tests required before merging?",
    ]),
    ("Project Structure & Organization", [
        "Is the project layout clear and modular?",
        "Are module boundaries and single responsibilities enforced?",
        "Is there any disorganization that could hinder onboarding or maintenance?",
        "Is technical debt (dead or duplicate code) being addressed?",
    ]),
]

ANTI_PATTERNS = [
    {
        "name": "Fragile Code",
        "description": (
            "Code that is easily broken by unrelated changes or updates. "
            "Symptoms: tight coupling, large functions, unclear boundaries, lack of tests. "
            "Consequences: bugs, firefighting, fear of change, loss of confidence."
        ),
        "remediation": (
            "Extract responsibilities into small, focused functions. "
            "Define clear interfaces. Start writing tests to prevent regressions."
        ),
    },
    {
        "name": "Lax Coding Standards",
        "description": (
            "Inconsistent style across the codebase makes code harder to read, maintain, and review. "
            "Symptoms: no style guide, lack of automated tooling, weak code review process."
        ),
        "remediation": (
            "Adopt a common style guide. Enforce formatting with tools. Include style checks in CI."
        ),
    },
    {
        "name": "Untested Code",
        "description": (
            "Code without tests leads to uncertainty about breaking existing behavior. "
            "Symptoms: tight deadlines, no testing culture, legacy code without tests."
        ),
        "remediation": (
            "Start small—add tests for core flows. Integrate a testing framework. "
            "Require tests for new features or bug fixes."
        ),
    },
    {
        "name": "Insecure Code",
        "description": (
            "Security flaws can let attackers steal data or shut down systems. "
            "Symptoms: skipping input validation, custom auth, no security audits."
        ),
        "remediation": (
            "Validate and sanitize all input. Use proven libraries for auth. "
            "Automate security scans."
        ),
    },
    {
        "name": "Disorganized Codebase",
        "description": (
            "A messy project is hard to navigate and reason about. "
            "Symptoms: no folder structure, god classes, copy-pasted code."
        ),
        "remediation": (
            "Define a clear project layout. Enforce module boundaries. "
            "Regularly review and pay down tech debt."
        ),
    },
]

def get_llm_provider(provider: str, model: str = None, **kwargs):
    """
    Get LLM provider using factory pattern.
    
    Args:
        provider: Provider name (openai, gemini, claude, local)
        model: Model name (optional, uses default if not provided)
        **kwargs: Additional provider-specific configuration
        
    Returns:
        LLM provider instance
    """
    return LLMProviderFactory.create_provider(provider, model, **kwargs)

def parse_unified_diff(diff_str: str):
    changes = []
    for line in diff_str.splitlines():
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        if line.startswith("@@"):
            continue
        if line.startswith("+"):
            changes.append({"type": "+", "content": line[1:]})
        elif line.startswith("-"):
            changes.append({"type": "-", "content": line[1:]})
        else:
            changes.append({"type": " ", "content": line})
    return changes

# Node: Generate review comments for a file
def review_file_node(state):
    llm_provider = state["llm_provider"]
    file_path = state["file_path"]
    diff_str = state["diff_str"]
    flake8_report = state.get("flake8_report", "")
    bandit_report = state.get("bandit_report", "")
    snyk_report = state.get("snyk_report", "")
    points_str = ""
    for section, points in REVIEW_POINTS:
        points_str += f"\n{section}:\n"
        for p in points:
            points_str += f"- {p}\n"
    prompt = (
        f"File: {file_path}\n"
        f"Diff:\n{diff_str}\n"
        f"Flake8 Linting Report (if any):\n{flake8_report}\n"
        f"Bandit Security Report (if any):\n{bandit_report}\n"
        f"Snyk Vulnerability Report (if any):\n{snyk_report}\n"
        f"Review Points and Anti-Patterns to check for:\n{points_str}\n"
        "Please provide detailed, actionable review comments for this diff, referencing the above. "
        "If you spot any anti-patterns, call them out and suggest concrete improvements."
    )
    system_prompt = "You are an expert engineering manager reviewing code changes."
    response = llm_provider.invoke_simple(prompt, system_prompt)
    state["review"] = response
    return state

# Node: Generate PR summary
def pr_summary_node(state):
    llm_provider = state["llm_provider"]
    files = state["files"]
    prompt = (
        f"Files changed: {list(files.keys())}\n"
        f"Guiding Principles: {TEAM_GUIDING_PRINCIPLES}\n"
        "Write a strategic PR summary (What/Why, Risks, Actions) for these changes."
    )
    
    system_prompt = "You are an expert engineering manager reviewing code changes."
    response = llm_provider.invoke_simple(prompt, system_prompt)
    state["pr_description"] = response
    return state

# Node: Aggregate results
def aggregate_node(state):
    # Collect all reviews and the PR description
    return {
        "comments": state["all_reviews"],
        "pr_description": state["pr_description"]
    }

# Node: Diff Generator
def diff_generator_node(state):
    repo_path = state.get("repo_path", ".")
    mode = state.get("mode", "branch")
    base = state.get("base", "main")
    target = state.get("target", "HEAD")
    commit_hash = state.get("commit_hash")
    agent = DiffGeneratorAgent(repo_path)
    if mode == "staged":
        diffs = agent.get_staged_diff()
    elif mode == "unstaged":
        diffs = agent.get_unstaged_diff()
    elif mode == "commit":
        if not commit_hash:
            raise ValueError("commit_hash required for commit mode")
        diffs = agent.get_commit_diff(commit_hash)
    else:
        diffs = agent.get_diff(base, target)
    state["files"] = diffs
    return state

def main(input_json_file=None, provider=None, model=None, **kwargs):
    # If input_json_file is provided, use it (legacy mode), else use diff_generator_node
    files = {}
    if input_json_file:
        with open(input_json_file, "r") as f:
            payload = json.load(f)
        files = payload.get("files", {})
    llm_provider = get_llm_provider(provider, model, **kwargs)
    graph = StateGraph()
    # Add diff generator node
    graph.add_node("diff_generator", diff_generator_node)
    graph.add_node("tool_agent", tool_agent_node)
    # For each file, add a review node (these will be added after diff generation)
    def make_review_node(fp, ds):
        return lambda state: review_file_node({**state, "file_path": fp, "diff_str": ds})
    # We'll add review nodes dynamically after diff generation
    graph.add_node("pr_summary", pr_summary_node)
    graph.add_node("aggregate", aggregate_node)
    # Set entry to diff_generator
    graph.set_entry("diff_generator")
    # After diff_generator, dynamically add review nodes or go to aggregate if no files
    graph.add_edge("diff_generator", "tool_agent")
    def after_tool_agent(state):
        files = state.get("files", {})
        file_paths = list(files.keys())
        if not file_paths:
            return "aggregate"
        # Add review nodes for each file
        for file_path in file_paths:
            graph.add_node(f"review_{file_path}", make_review_node(file_path, files[file_path]))
        # Add edges between review nodes
        for i, file_path in enumerate(file_paths):
            if i < len(file_paths) - 1:
                graph.add_edge(f"review_{file_path}", f"review_{file_paths[i+1]}")
            else:
                graph.add_edge(f"review_{file_path}", "pr_summary")
        graph.add_edge("pr_summary", "aggregate")
        graph.set_exit("aggregate")
        return f"review_{file_paths[0]}"
    graph.add_edge("tool_agent", after_tool_agent)
    # Initial state
    state = {
        "llm_provider": llm_provider,
        "repo_path": kwargs.get("repo_path", "."),
        "mode": kwargs.get("mode", "branch"),
        "base": kwargs.get("base", "main"),
        "target": kwargs.get("target", "HEAD"),
        "commit_hash": kwargs.get("commit_hash"),
        "all_reviews": []
    }
    def on_node(node_name, state):
        if node_name == "diff_generator":
            return diff_generator_node(state)
        if node_name == "tool_agent":
            return tool_agent_node(state)
        if node_name.startswith("review_"):
            result = review_file_node(state)
            state.setdefault("all_reviews", []).append({
                "file": state["file_path"],
                "review": result["review"]
            })
            return state
        elif node_name == "pr_summary":
            return pr_summary_node(state)
        elif node_name == "aggregate":
            return aggregate_node(state)
        return state
    result = graph.run(state, on_node=on_node)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    import sys
    # Accept both legacy (input_json_file) and new (repo_path, mode, etc.) usage
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        provider = sys.argv[2]
        model = sys.argv[3] if len(sys.argv) > 3 else None
        main(input_file, provider, model)
    else:
        # New usage: all config via kwargs or environment
        # Example: python eng_manager_review_agent.py --repo-path . --mode branch --base main --target HEAD --provider openai --model gpt-4
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--repo-path', default='.', help='Path to git repository (default: current directory)')
        parser.add_argument('--mode', choices=['branch', 'staged', 'unstaged', 'commit'], default='branch', help='Diff mode (default: branch)')
        parser.add_argument('--base', default='main', help='Base reference for branch comparison (default: main)')
        parser.add_argument('--target', default='HEAD', help='Target reference for branch comparison (default: HEAD)')
        parser.add_argument('--commit-hash', help='Commit hash for commit mode')
        parser.add_argument('--provider', required=True, help='LLM provider (openai, gemini, claude, local)')
        parser.add_argument('--model', help='Model name (optional)')
        args = parser.parse_args()
        main(None, args.provider, args.model,
             repo_path=args.repo_path,
             mode=args.mode,
             base=args.base,
             target=args.target,
             commit_hash=args.commit_hash) 