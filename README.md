# Engineering Manager Code Review Agent

This project is an **AI-powered code review assistant** designed to help engineering managers and teams perform high-quality, strategic code reviews. It leverages large language models (LLMs) to analyze code diffs, provide actionable review comments, and generate PR summaries based on best practices and team guiding principles.

## Features
- Automated, detailed code review comments for each file in a pull request
- Strategic PR summary generation (What/Why, Risks, Actions)
- Checks for anti-patterns and adherence to team principles
- Supports multiple LLM providers: OpenAI (GPT), Google Gemini, Ollama (local models)
- Customizable review points and anti-patterns
- **Automatic diff generation** from git repositories
- **Combined workflow** for seamless code review automation

## How It Works
1. **Automatic diff generation** from git repository (branch comparison, staged changes, commits)
2. Runs each file diff through an LLM, guided by review points and anti-patterns
3. Aggregates review comments and generates a PR summary
4. Outputs a structured JSON with all comments and the PR description

## Installation
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd em-code-reviewer
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set API keys as environment variables** (as needed):
   - For OpenAI: `OPENAI_API_KEY`
   - For Gemini: `GEMINI_API_KEY`
   - Ollama runs locally and does not require an API key

## Usage

### Quick Start (Recommended)
Use the combined auto-review script for the easiest workflow:

```bash
# Review current branch vs main using OpenAI
python auto_review.py --provider openai --model gpt-4

# Review staged changes using Ollama
python auto_review.py --mode staged --provider ollama --model llama3

# Review specific commit using Gemini
python auto_review.py --mode commit --commit-hash abc123 --provider gemini
```

### Manual Workflow
If you prefer to generate the diff manually:

1. **Generate diff.json:**
   ```bash
   # Compare current branch with main
   python diff_generator_agent.py --base main --target HEAD
   
   # Generate diff for staged changes
   python diff_generator_agent.py --mode staged
   
   # Generate diff for specific commit
   python diff_generator_agent.py --mode commit --commit-hash abc123
   ```

2. **Run code review:**
   ```bash
   python eng_manager_review_agent.py diff.json openai gpt-4
   ```

### Diff Generation Options
The diff generator supports multiple scenarios:

- **Branch comparison** (default): Compare two branches or commits
- **Staged changes**: Review changes that are staged for commit
- **Unstaged changes**: Review working directory changes
- **Commit review**: Review a specific commit

### Example Commands

#### Auto Review (Combined Workflow)
```bash
# Review current branch vs main
python auto_review.py --provider openai --model gpt-4

# Review staged changes only
python auto_review.py --mode staged --provider ollama --model llama3

# Review specific commit
python auto_review.py --mode commit --commit-hash abc123 --provider gemini

# Review branch comparison with custom output
python auto_review.py --base feature-branch --target main --provider openai --output my_review.json

# Generate diff only (skip review)
python auto_review.py --mode staged --provider openai --skip-review
```

#### Manual Diff Generation
```bash
# Compare current branch with main
python diff_generator_agent.py --base main --target HEAD

# Generate diff for staged changes
python diff_generator_agent.py --mode staged

# Generate diff for specific commit
python diff_generator_agent.py --mode commit --commit-hash abc123

# Compare two branches
python diff_generator_agent.py --base feature-branch --target main
```

### Example Input JSON
```json
{
  "files": {
    "src/foo.py": "@@ -1,6 +1,8 @@\n import os\n+import sys\n def foo():\n     pass\n+def bar():\n+    return True\n"
  }
}
```

### Output
The script prints a JSON object with:
- `comments`: List of review comments per file
- `pr_description`: Strategic PR summary

## Supported LLM Providers
- **OpenAI**: GPT-4, GPT-3.5, etc. (`openai`)
- **Google Gemini**: Gemini Pro (`gemini`)
- **Ollama**: Local models like Llama3 (`ollama`)

## Customization
- **Review points and anti-patterns** can be edited in `eng_manager_review_agent.py` to match your team's needs.
- Extend or modify the review logic by editing the review nodes in the code.
- Customize diff generation behavior in `diff_generator_agent.py`.

## License
MIT License (add your own if different)

## Contact
For questions or suggestions, open an issue or contact the maintainer. 