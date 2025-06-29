# Engineering Manager Code Review Agent

This project is an **AI-powered code review assistant** designed to help engineering managers and teams perform high-quality, strategic code reviews. It leverages large language models (LLMs) to analyze code diffs, provide actionable review comments, and generate PR summaries based on best practices and team guiding principles.

## Features
- Automated, detailed code review comments for each file in a pull request
- Strategic PR summary generation (What/Why, Risks, Actions)
- Checks for anti-patterns and adherence to team principles
- Supports multiple LLM providers: OpenAI (GPT), Google Gemini, Ollama (local models)
- Customizable review points and anti-patterns

## How It Works
1. Accepts a JSON file describing changed files and their diffs
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
Run the agent from the command line:

```bash
python eng_manager_review_agent.py <input_json_file> <provider> [<model>]
```

- `<input_json_file>`: Path to a JSON file describing the files and their diffs
- `<provider>`: LLM provider (`openai`, `gemini`, or `ollama`)
- `<model>`: (Optional) Model name (e.g., `gpt-4`, `gemini-pro`, `llama3`)

### Example Input JSON
```json
{
  "files": {
    "src/foo.py": "@@ -1,6 +1,8 @@\n import os\n+import sys\n def foo():\n     pass\n+def bar():\n+    return True\n"
  }
}
```

### Example Command
```bash
python eng_manager_review_agent.py my_pr_diff.json openai gpt-4
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

## License
MIT License (add your own if different)

## Contact
For questions or suggestions, open an issue or contact the maintainer. 