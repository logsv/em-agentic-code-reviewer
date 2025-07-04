import os
from tools import TOOLS

def detect_repo_types(repo_path):
    files = set(os.listdir(repo_path))
    types = set()
    # Python detection
    if any(f.endswith(".py") for f in files) or "requirements.txt" in files or "pyproject.toml" in files:
        types.add("python")
    # Node.js detection
    if "package.json" in files or any(f.endswith(".js") or f.endswith(".ts") for f in files):
        types.add("nodejs")
    # Go detection
    if "go.mod" in files or any(f.endswith(".go") for f in files):
        types.add("golang")
    # Recursively check subdirectories for monorepos
    for root, dirs, subfiles in os.walk(repo_path):
        subfiles = set(subfiles)
        if any(f.endswith(".py") for f in subfiles) or "requirements.txt" in subfiles or "pyproject.toml" in subfiles:
            types.add("python")
        if "package.json" in subfiles or any(f.endswith(".js") or f.endswith(".ts") for f in subfiles):
            types.add("nodejs")
        if "go.mod" in subfiles or any(f.endswith(".go") for f in subfiles):
            types.add("golang")
    if not types:
        types.add("unknown")
    return list(types)

def get_tools_for_repo_types(repo_types):
    toolset = set()
    for repo_type in repo_types:
        if repo_type == "python":
            toolset.update(["flake8", "bandit", "snyk", "mypy", "pylint"])
        if repo_type == "nodejs":
            toolset.update(["eslint", "npm_audit", "snyk"])
        if repo_type == "golang":
            toolset.update(["golint", "gosec", "govulncheck", "snyk"])
    if not toolset:
        toolset = set(TOOLS.keys())
    return list(toolset) 