import os
import json
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from llm_providers.factory import LLMProviderFactory

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
    points_str = ""
    for section, points in REVIEW_POINTS:
        points_str += f"\n{section}:\n"
        for p in points:
            points_str += f"- {p}\n"

    prompt = (
        f"File: {file_path}\n"
        f"Diff:\n{diff_str}\n"
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

def main(input_json_file, provider, model=None, **kwargs):
    with open(input_json_file, "r") as f:
        payload = json.load(f)
    files = payload.get("files", {})

    llm_provider = get_llm_provider(provider, model, **kwargs)

    # Build the graph
    graph = StateGraph()
    # For each file, add a review node
    for file_path, diff_str in files.items():
        def make_review_node(fp, ds):
            return lambda state: review_file_node({**state, "file_path": fp, "diff_str": ds})
        graph.add_node(f"review_{file_path}", make_review_node(file_path, diff_str))
    # Add PR summary node
    graph.add_node("pr_summary", pr_summary_node)
    # Add aggregate node
    graph.add_node("aggregate", aggregate_node)

    # Define transitions
    # Start with first file review
    file_paths = list(files.keys())
    if not file_paths:
        print("No files to review.")
        return
    for i, file_path in enumerate(file_paths):
        if i == 0:
            graph.set_entry(f"review_{file_path}")
        if i < len(file_paths) - 1:
            # After each review, go to next review
            graph.add_edge(f"review_{file_path}", f"review_{file_paths[i+1]}")
        else:
            # After last review, go to pr_summary
            graph.add_edge(f"review_{file_path}", "pr_summary")
    # After pr_summary, go to aggregate
    graph.add_edge("pr_summary", "aggregate")
    # End after aggregate
    graph.set_exit("aggregate")

    # Initial state
    state = {
        "llm_provider": llm_provider,
        "files": files,
        "all_reviews": []
    }

    # Run the graph
    def on_node(node_name, state):
        if node_name.startswith("review_"):
            result = review_file_node(state)
            # Collect reviews
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
    if len(sys.argv) < 3:
        print("Usage: python eng_manager_review_agent.py <input_json_file> <provider> [<model>]")
        print("Providers:", ", ".join(LLMProviderFactory.get_supported_providers()))
        print("\nProvider Info:")
        for name, info in LLMProviderFactory.get_provider_info().items():
            print(f"  {name}: {info['default_model']} (default)")
        exit(1)
    input_file = sys.argv[1]
    provider = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else None
    main(input_file, provider, model) 