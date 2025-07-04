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

# Python: mypy (type checking)
def run_mypy(repo_path):
    result = subprocess.run([
        "mypy", repo_path
    ], capture_output=True, text=True)
    return result.stdout

# Python: pylint (linting, code quality)
def run_pylint(repo_path):
    result = subprocess.run([
        "pylint", repo_path
    ], capture_output=True, text=True)
    return result.stdout

# Node.js: eslint (linting)
def run_eslint(repo_path):
    result = subprocess.run([
        "npx", "eslint", repo_path, "--format", "json"
    ], capture_output=True, text=True)
    return result.stdout

# Node.js: npm audit (vulnerability check)
def run_npm_audit(repo_path):
    result = subprocess.run([
        "npm", "audit", "--json"], cwd=repo_path, capture_output=True, text=True)
    return result.stdout

# Go: golint (linting)
def run_golint(repo_path):
    result = subprocess.run([
        "golint", repo_path
    ], capture_output=True, text=True)
    return result.stdout

# Go: gosec (security)
def run_gosec(repo_path):
    result = subprocess.run([
        "gosec", "./..."], cwd=repo_path, capture_output=True, text=True)
    return result.stdout

# Go: govulncheck (vulnerability check)
def run_govulncheck(repo_path):
    result = subprocess.run([
        "govulncheck", "./..."], cwd=repo_path, capture_output=True, text=True)
    return result.stdout

TOOLS = {
    "flake8": run_flake8,
    "bandit": run_bandit,
    "snyk": run_snyk,
    "mypy": run_mypy,
    "pylint": run_pylint,
    "eslint": run_eslint,
    "npm_audit": run_npm_audit,
    "golint": run_golint,
    "gosec": run_gosec,
    "govulncheck": run_govulncheck,
} 