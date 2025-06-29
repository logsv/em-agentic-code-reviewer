# Engineering Manager Code Review Agent

This project is an **AI-powered code review assistant** designed to help engineering managers and teams perform high-quality, strategic code reviews. It leverages large language models (LLMs) to analyze code diffs, provide actionable review comments, and generate PR summaries based on best practices and team guiding principles.

## 🏗️ Architecture

Built following **SOLID principles** and **design patterns**:
- **Strategy Pattern**: Different LLM providers implement the same interface
- **Factory Pattern**: Centralized provider creation and management
- **Open/Closed Principle**: Easy to add new providers without modifying existing code
- **Single Responsibility**: Each provider handles its own configuration and initialization
- **Dependency Inversion**: High-level modules don't depend on low-level modules

## Features
- Automated, detailed code review comments for each file in a pull request
- Strategic PR summary generation (What/Why, Risks, Actions)
- Checks for anti-patterns and adherence to team principles
- **Multiple LLM Providers**: OpenAI, Google Gemini, Anthropic Claude, Local Models
- **Popular Local Models**: DeepSeek R1, Llama3, CodeLlama, Mistral, and more
- Customizable review points and anti-patterns
- **Automatic diff generation** from git repositories
- **Combined workflow** for seamless code review automation
- **GitHub Actions integration** for automated PR reviews
- **Ngrok tunneling** for remote local model access

## How It Works
1. **Automatic diff generation** from git repository (branch comparison, staged changes, commits)
2. Runs each file diff through an LLM, guided by review points and anti-patterns
3. Aggregates review comments and generates a PR summary
4. Outputs a structured JSON with all comments and the PR description

## Installation

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd em-code-reviewer
pip install -r requirements.txt
```

### 2. Set API Keys (for cloud providers)
```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# For Google Gemini
export GEMINI_API_KEY="your-gemini-api-key"

# For Anthropic Claude
export ANTHROPIC_API_KEY="your-claude-api-key"
```

### 3. Local Models Setup (Optional)

#### Install Ollama

**macOS:**
```bash
# Using Homebrew
brew install ollama

# Or download from website
curl -fsSL https://ollama.ai/install.sh | sh
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
```powershell
# Download from https://ollama.ai/download
# Or using winget
winget install Ollama.Ollama
```

#### Pull Popular Models
```bash
# DeepSeek R1 (excellent for code review)
ollama pull deepseek-r1

# Llama3 (general purpose)
ollama pull llama3

# CodeLlama (code-specific)
ollama pull codellama

# Mistral (fast and efficient)
ollama pull mistral
```

#### Start Ollama Server

**Option 1: Using provided scripts**
```bash
# Unix/macOS
chmod +x start_ollama.sh
./start_ollama.sh --daemon

# Windows PowerShell
.\start_ollama.ps1 -Daemon

# Python script (cross-platform)
python start_ollama.py --daemon
```

**Option 2: Manual startup**
```bash
# Unix/macOS
export OLLAMA_ORIGINS="*"
ollama serve &

# Windows PowerShell
$env:OLLAMA_ORIGINS="*"
Start-Process ollama -ArgumentList "serve"
```

#### Remote Access with Ngrok (Optional)

For accessing local models from remote machines or CI/CD:

```bash
# Install ngrok
# macOS: brew install ngrok
# Linux: Download from https://ngrok.com/download

# Start Ollama server
./start_ollama.sh --daemon

# Create tunnel to Ollama
ngrok http 11434

# Use the ngrok URL in your environment
export OLLAMA_BASE_URL="https://your-ngrok-url.ngrok.io"
```

## Usage

### Quick Start (Recommended)
Use the combined auto-review script for the easiest workflow:

```bash
# Review current branch vs main using OpenAI
python auto_review.py --provider openai --model gpt-4

# Review staged changes using local deepseek-r1
python auto_review.py --mode staged --provider local --model deepseek-r1

# Review specific commit using Claude
python auto_review.py --mode commit --commit-hash abc123 --provider claude

# List all available providers and models
python auto_review.py --list-providers
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

### GitHub Actions Integration

#### Setup
1. **Add repository secrets** in your GitHub repository settings:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `ANTHROPIC_API_KEY`: Your Anthropic Claude API key

2. **Copy the workflow files** to your repository:
   - `.github/workflows/code-review.yml` (for OpenAI/Gemini/Claude)
   - `.github/workflows/code-review-ollama.yml` (for local models)

#### Automatic PR Reviews
The workflows automatically run on:
- **Pull request opened**
- **Pull request updated**
- **Pull request reopened**

#### Workflow Features
- 🤖 **Automatic commenting**: Reviews are posted as PR comments
- 📊 **Artifact storage**: Review results are saved as workflow artifacts
- 🔄 **Flexible triggers**: Works with any branch comparison
- ⚡ **Fast execution**: Optimized for quick feedback

#### Example PR Comment
```
## 🤖 AI Code Review Results

### 📋 PR Summary
This PR introduces a new authentication system with improved security...

### 📝 File Reviews

#### 📄 src/auth.py
```
✅ Good separation of concerns
⚠️ Consider adding input validation
🔧 Suggested: Add error handling for edge cases
```

---
*This review was generated automatically using AI-powered code review tools.*
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
python auto_review.py --mode staged --provider local --model deepseek-r1

# Review specific commit
python auto_review.py --mode commit --commit-hash abc123 --provider claude

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

### Cloud Providers
- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- **Google Gemini**: Gemini Pro, Gemini 1.5 Pro, Gemini 1.5 Flash
- **Anthropic Claude**: Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku

### Local Models (via Ollama)
- **DeepSeek R1**: Excellent for code review and analysis
- **Llama3**: Meta's general-purpose model
- **CodeLlama**: Code-specific Llama variant
- **Mistral**: Fast and efficient 7B model
- **Mixtral**: High-performance 8x7B model
- **Neural Chat**: Intel's conversational model
- **Qwen2**: Alibaba's Qwen2 model
- **Phi-3**: Microsoft's Phi-3 model

## Customization
- **Review points and anti-patterns** can be edited in `eng_manager_review_agent.py` to match your team's needs.
- Extend or modify the review logic by editing the review nodes in the code.
- Customize diff generation behavior in `diff_generator_agent.py`.
- **Add new LLM providers** by implementing the `BaseLLMProvider` interface.
- Modify GitHub Actions workflows to fit your CI/CD pipeline.

## Development

### Adding New LLM Providers
1. Create a new provider class in `llm_providers/`
2. Extend `BaseLLMProvider` and implement required methods
3. Register the provider in `LLMProviderFactory`

Example:
```python
from .base_provider import BaseLLMProvider

class MyProvider(BaseLLMProvider):
    def _validate_config(self) -> bool:
        # Validate configuration
        return True
    
    def _initialize_llm(self):
        # Initialize your LLM
        return MyLLM(model=self.model, **self.config)
    
    @classmethod
    def get_supported_models(cls) -> List[str]:
        return ["my-model-1", "my-model-2"]
    
    @classmethod
    def get_provider_name(cls) -> str:
        return "my-provider"
```

### Architecture Benefits
- **Extensible**: Easy to add new providers without changing existing code
- **Testable**: Each provider can be tested independently
- **Maintainable**: Clear separation of concerns
- **Configurable**: Flexible configuration for different environments

## License
MIT License (add your own if different)

## Contact
For questions or suggestions, open an issue or contact the maintainer. 