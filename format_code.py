#!/usr/bin/env python3
"""
Code formatting helper script.

This script automates the process of running formatters and linters
to help identify and fix code style issues.
"""

# Standard library imports
import argparse
import difflib
import filecmp
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from shutil import copy2

import requests  # For API calls to LLMs


def run_command(command, description, capture=True):
    """Run a shell command and print its output."""
    print(f"\n\033[1;34m{description}\033[0m")
    print(f"Running: {' '.join(command)}\n")

    if capture:
        # Add explicit encoding to prevent charmap codec errors
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",  # Explicitly use UTF-8 encoding
            errors="replace",  # Replace characters that can't be decoded
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr and result.returncode != 0:
            print(f"\033[1;31mErrors:\033[0m\n{result.stderr}")
        elif result.stderr:
            print(result.stderr)

        return result.returncode, result.stdout, result.stderr
    else:
        # Run without capturing to show output in real-time
        result = subprocess.run(command)
        return result.returncode, "", ""


def get_python_files(directory="."):
    """Get all Python files in the directory recursively."""
    files = []
    # Define common virtual environment directory names to exclude
    venv_dirs = {"venv", ".venv", "env", ".env", "virtualenv", "__pycache__"}

    for path in Path(directory).rglob("*.py"):
        # Skip files in virtual environment directories
        if any(vdir in path.parts for vdir in venv_dirs):
            continue
        files.append(str(path))
    return files


def count_issues_by_file(flake8_output):
    """Parse flake8 output and count issues by file."""
    file_issues = {}

    if not flake8_output:
        return file_issues

    for line in flake8_output.splitlines():
        match = re.match(r"^(.+?):(\d+):(\d+): ([A-Z]\d+) (.+)$", line)
        if match:
            filepath, line_num, col, error_code, error_msg = match.groups()

            if filepath not in file_issues:
                file_issues[filepath] = {}

            if error_code not in file_issues[filepath]:
                file_issues[filepath][error_code] = 0

            file_issues[filepath][error_code] += 1

    return file_issues


def check_if_file_changed(filepath):
    """Check if a file was modified by creating a backup and comparing."""
    # Skip virtual environment files
    if any(
        vdir in filepath
        for vdir in [
            "venv",
            ".venv",
            "env",
            ".env",
            "virtualenv",
            "__pycache__",
        ]
    ):
        print(f"\033[1;33mSkipping virtual environment file: {filepath}\033[0m")
        return False

    # Create a temporary backup of the file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
        copy2(filepath, temp_path)

    # Run black on the file with virtual environment exclusions
    subprocess.run(
        [
            "black",
            "--exclude",
            r"(\.venv|venv|env|\.env|virtualenv|__pycache__)",
            filepath,
        ],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )

    # Compare the original (backup) with the potentially modified file
    changed = not filecmp.cmp(temp_path, filepath)

    # Clean up the temporary file
    os.unlink(temp_path)

    return changed


def fix_one_file(filepath, use_llm=False):
    """Focus on fixing one file at a time."""
    print(f"\n\033[1;35mFocusing on file: {filepath}\033[0m")

    # Check if the file exists
    if not os.path.isfile(filepath):
        print(f"\033[1;31mError: File {filepath} does not exist\033[0m")
        return filepath

    # First check if Black would make any changes
    will_change = check_if_file_changed(filepath)

    if will_change:
        print("\033[1;32mBlack will modify this file.\033[0m")
    else:
        print("\033[1;33mBlack formatting: No changes needed.\033[0m")

    # Ask for confirmation before applying Black
    choice = input("\nRun Black formatter on this file? (y/n): ")
    if choice.lower() == "y":
        print("\nApplying Black formatter:")
        subprocess.run(
            ["black", "--config=pyproject.toml", filepath], capture_output=False
        )
    else:
        print("\033[1;33mSkipping Black formatter.\033[0m")

    # Ask for confirmation before applying isort
    choice = input("\nRun isort on this file? (y/n): ")
    if choice.lower() == "y":
        print("\nApplying isort:")
        subprocess.run(
            ["isort", "--settings-path=pyproject.toml", filepath],
            capture_output=False,
        )
    else:
        print("\033[1;33mSkipping isort.\033[0m")

    # Run flake8 on this file to see remaining issues
    print("\nChecking for remaining issues:")
    flake8_process = subprocess.run(["flake8", filepath], capture_output=False)

    if flake8_process.returncode == 0:
        print("Flake8 linting: ✅ No issues")
    else:
        print("Flake8 linting: ❌ Issues remaining (see above)")

        if use_llm:
            print("\nAttempting to fix remaining issues with AI assistance...")
            fix_with_llm(filepath)
        else:
            print("You'll need to fix these issues manually.")
            print("Run with --ai-assist to try fixing with AI.")

    return filepath


def fix_with_llm(filepath):
    """Use an LLM to suggest fixes for remaining issues in the file."""
    # Get the current content of the file
    with open(filepath, "r", encoding="utf-8") as f:
        file_content = f.read()

    # Create a backup of the file
    backup_path = f"{filepath}.bak"
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(file_content)

    # Run flake8 to get specific errors
    flake8_result = subprocess.run(
        ["flake8", filepath],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    errors = flake8_result.stdout

    # Select a portion of the file if it's too large
    file_selection = file_content
    if len(file_content) > 4000:
        print("File is large. Selecting relevant portions...")
        # Extract error line numbers
        line_numbers = []
        for line in errors.splitlines():
            match = re.match(r"^.+?:(\d+):", line)
            if match:
                line_numbers.append(int(match.group(1)))

        if line_numbers:
            # Select a window around the error lines
            all_lines = file_content.splitlines()
            window_size = 10  # Lines before and after each error
            selected_lines = set()

            for line_num in line_numbers:
                start = max(0, line_num - window_size - 1)
                end = min(len(all_lines), line_num + window_size)
                selected_lines.update(range(start, end))

            selected_lines = sorted(selected_lines)
            file_selection = "\n".join([all_lines[i] for i in selected_lines])

            # Add line number markers
            file_selection = (
                f"# Selected portions of {filepath}\n{file_selection}"
            )

    # Prepare the prompt for the LLM - make it much more specific
    prompt = (
        f"Fix ONLY the following Python code issues:\n\n"
        f"File: {filepath}\n\n"
        f"Errors:\n{errors}\n\n"
        f"Please ONLY fix the specific issues mentioned in the errors above. "
        f"DO NOT refactor, rewrite, or modify any code that doesn't need "
        f"to be fixed.\n\n"
        f"For example:\n"
        f'- If the error is "D400 First line should end with a period", '
        f"just add a period at the end of the docstring first line\n"
        f'- If the error is "B027 __init__ is an empty method in an '
        f'abstract base class", just add @abstractmethod decorator\n'
        f"- Leave all other code completely unchanged\n\n"
        f"File content:\n```python\n{file_selection}\n```\n\n"
        f"Please show ONLY the specific lines that need to be changed, with "
        f"minimal modifications to fix the errors. Do NOT rewrite the entire "
        f"file."
    )

    # Use the preferred LLM service
    llm_service = get_llm_service()
    if llm_service == "local":
        response = call_local_llm(prompt)
    elif llm_service == "openai":
        response = call_openai(prompt)
    elif llm_service == "anthropic":
        response = call_anthropic(prompt)
    else:
        print(f"\033[1;31mUnsupported LLM service: {llm_service}\033[0m")
        return

    # Extract code from the response
    suggested_code = extract_code_from_response(response)

    if not suggested_code:
        print(
            "\033[1;31mCouldn't extract valid code from the LLM response\033[0m"
        )
        return

    # Show a diff of the changes
    show_diff(file_content, suggested_code, filepath)

    # Ask user if they want to apply the changes
    choice = input("\nApply these changes? (y/n): ")

    if choice.lower() == "y":
        # Apply the changes
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(suggested_code)
        print(f"\033[1;32mChanges applied to {filepath}\033[0m")
    else:
        print("\033[1;33mChanges not applied. Original file preserved.\033[0m")
        # Restore from backup
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(file_content)

    # Clean up backup
    os.remove(backup_path)


def get_llm_service():
    """Get the LLM service from config or environment."""
    config_file = os.path.join(os.path.dirname(__file__), "llm_config.json")

    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                return config.get("service", "openai")
        except Exception:
            pass

    # Check environment variables as fallback
    if "LLM_SERVICE" in os.environ:
        return os.environ["LLM_SERVICE"]

    # Default to OpenAI
    return "openai"


def call_openai(prompt):
    """Call OpenAI API to get suggestions."""
    # First try to get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")

    # If not in environment, try to get from config file
    if not api_key:
        config_file = os.path.join(os.path.dirname(__file__), "llm_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                    api_keys = config.get("api_keys", {})
                    api_key = api_keys.get("openai")
            except Exception as e:
                print(
                    f"\033[1;31mError reading API key from config: {e}\033[0m"
                )

    if not api_key:
        print(
            "\033[1;31mOpenAI API key not found. Set the OPENAI_API_KEY "
            "environment variable or add it to llm_config.json.\033[0m"
        )
        return ""

    try:
        # Updated code for OpenAI API v1.0.0+
        # Third-party imports
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4",  # Use an appropriate model
            messages=[
                {
                    "role": "system",
                    "content": "You are a Python code formatting assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        # Updated way to access response content
        return response.choices[0].message.content
    except Exception as e:
        print(f"\033[1;31mError calling OpenAI API: {str(e)}\033[0m")
        return ""


def call_anthropic(prompt):
    """Call Anthropic API to get suggestions."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "\033[1;31mAnthropic API key not found. Set the ANTHROPIC_API_KEY "
            "environment variable.\033[0m"
        )
        return ""

    try:
        headers = {"Content-Type": "application/json", "X-API-Key": api_key}

        data = {
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "model": "claude-2",
            "max_tokens_to_sample": 4000,
            "temperature": 0.3,
        }

        response = requests.post(
            "https://api.anthropic.com/v1/complete", headers=headers, json=data
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("completion", "")
        else:
            print(
                f"\033[1;31mError from Anthropic API: {response.status_code}\n"
                f"{response.text}\033[0m"
            )
            return ""
    except Exception as e:
        print(f"\033[1;31mError calling Anthropic API: {str(e)}\033[0m")
        return ""


def call_local_llm(prompt):
    """Call a local LLM via API to get suggestions."""
    # Get the local URL from config
    config_file = os.path.join(os.path.dirname(__file__), "llm_config.json")
    local_url = None
    local_model = "codellama"  # Default to codellama for code formatting

    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                local_url = config.get("local_url")
                models = config.get("models", {})
                local_model = models.get("local", local_model)
        except Exception as e:
            print(f"\033[1;31mError reading local URL from config: {e}\033[0m")

    if not local_url:
        print(
            "\033[1;31mLocal LLM URL not configured. Run with --configure-llm"
            "\033[0m"
        )
        return ""

    try:
        print(f"Using local LLM at {local_url} with model {local_model}")

        # First, check available models
        try:
            list_response = requests.get(f"{local_url}/api/tags")
            if list_response.status_code == 200:
                models_list = list_response.json().get("models", [])
                model_names = [model.get("name") for model in models_list]

                if not model_names:
                    print(
                        "\033[1;33mNo models found on the Ollama server.\033[0m"
                    )
                    print(
                        "\033[1;33mPlease install a model using "
                        "'ollama pull codellama' or similar.\033[0m"
                    )
                    return ""

                if local_model not in model_names:
                    print(
                        f"\033[1;33mModel '{local_model}' not found on Ollama "
                        f"server.\033[0m"
                    )
                    print(
                        f"\033[1;33mAvailable models: "
                        f"{', '.join(model_names)}\033[0m"
                    )
                    print(
                        f"\033[1;33mInstall with: ollama pull {local_model}"
                        f"\033[0m"
                    )

                    # Try to fall back to any coding-related model
                    coding_models = [
                        m
                        for m in model_names
                        if any(
                            name in m.lower()
                            for name in [
                                "code",
                                "llama",
                                "starcoder",
                                "deepseek",
                            ]
                        )
                    ]

                    if coding_models:
                        fallback_model = coding_models[0]
                        print(
                            f"\033[1;33mFalling back to available model: "
                            f"{fallback_model}\033[0m"
                        )
                        local_model = fallback_model
                    else:
                        return ""
        except Exception as e:
            print(f"\033[1;33mCouldn't check available models: {e}\033[0m")

        # Ollama API format
        data = {"model": local_model, "prompt": prompt, "stream": False}

        # The correct endpoint for Ollama
        response = requests.post(f"{local_url}/api/generate", json=data)

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        elif (
            response.status_code == 404
            and "model not found" in response.text.lower()
        ):
            print(
                f"\033[1;31mModel '{local_model}' not found on the Ollama "
                f"server.\033[0m"
            )
            print(
                "\033[1;33mTo install it, run this command in your terminal:"
                "\033[0m"
            )
            print(f"\033[1;33mollama pull {local_model}\033[0m")
            return ""
        else:
            print(
                f"\033[1;31mAPI call failed: {response.status_code}\n"
                f"{response.text}\033[0m"
            )
            return ""

    except Exception as e:
        print(f"\033[1;31mError calling local LLM: {str(e)}\033[0m")
        return ""


def extract_code_from_response(response):
    """Extract code blocks from the LLM response."""
    # Look for ```python ... ``` blocks
    code_blocks = re.findall(
        r"```(?:python)?\s*(.*?)\s*```", response, re.DOTALL
    )

    if code_blocks:
        # Return the longest code block (assuming it's the full solution)
        return max(code_blocks, key=len).strip()

    return ""


def show_diff(original, modified, filepath):
    """Show a diff between the original and modified code."""
    original_lines = original.splitlines()
    modified_lines = modified.splitlines()

    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=f"{filepath} (original)",
        tofile=f"{filepath} (modified)",
        lineterm="",
    )

    print("\n\033[1;34mChanges suggested by AI:\033[0m")
    for line in diff:
        if line.startswith("+"):
            print(f"\033[0;32m{line}\033[0m")  # Green for additions
        elif line.startswith("-"):
            print(f"\033[0;31m{line}\033[0m")  # Red for deletions
        elif line.startswith("^"):
            print(f"\033[0;36m{line}\033[0m")  # Cyan for change markers
        elif line.startswith("@@"):
            print(f"\033[1;35m{line}\033[0m")  # Purple for line headers
        else:
            print(line)


def configure_llm():
    """Configure LLM settings."""
    config = {
        "service": "openai",  # Default service
        "models": {
            "openai": "gpt-4",
            "anthropic": "claude-2",
            "local": "llama2",
        },
    }

    print("\n\033[1;34mConfiguring AI Assistant\033[0m")
    print("Select LLM service:")
    print("1. OpenAI (GPT-4)")
    print("2. Anthropic (Claude)")
    print("3. Local LLM")

    choice = input("Enter choice (1-3): ")

    if choice == "1":
        config["service"] = "openai"
        api_key = input(
            "Enter OpenAI API key (leave blank to use environment variable): "
        )
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
    elif choice == "2":
        config["service"] = "anthropic"
        api_key = input(
            "Enter Anthropic API key (leave blank to use environment variable):"
        )
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
    elif choice == "3":
        config["service"] = "local"
        url = input("Enter local LLM API URL: ")
        if url:
            config["local_url"] = url

    # Save config
    config_file = os.path.join(os.path.dirname(__file__), "llm_config.json")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\033[1;32mConfiguration saved to {config_file}\033[0m")


def check_tool_exists(tool_name):
    """Check if a command-line tool is available in the PATH."""
    try:
        # Use 'where' on Windows or 'which' on Unix-like systems
        if os.name == "nt":  # Windows
            result = subprocess.run(
                ["where", tool_name], capture_output=True, text=True
            )
        else:  # Unix/Linux/Mac
            result = subprocess.run(
                ["which", tool_name], capture_output=True, text=True
            )

        return result.returncode == 0
    except Exception:
        return False


def install_missing_tools():
    """Install required tools if they're missing."""
    missing_tools = []

    # Check for essential tools
    if not check_tool_exists("flake8"):
        missing_tools.append("flake8")

    if not check_tool_exists("black"):
        missing_tools.append("black")

    # Try to install missing tools if any
    if missing_tools:
        print(
            "\n\033[1;31mMissing required tools: "
            f"{', '.join(missing_tools)}\033[0m"
        )
        print("\nAttempting to install them...")

        try:
            for tool in missing_tools:
                print(f"\nInstalling {tool}...")
                if tool == "flake8":
                    # Install flake8 and its plugins
                    subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "install",
                            "flake8==6.1.0",
                            "flake8-docstrings==1.7.0",
                            "flake8-import-order==0.18.2",
                            "flake8-bugbear==23.9.16",
                        ],
                        check=True,
                    )
                else:
                    # Install other tools directly
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", tool],
                        check=True,
                    )

            print("\n\033[1;32mTools installed successfully!\033[0m")
            return True
        except Exception as e:
            print(f"\n\033[1;31mFailed to install tools: {str(e)}\033[0m")
            print("\nPlease install them manually:")
            print(
                "pip install flake8==6.1.0 flake8-docstrings==1.7.0 "
                "flake8-import-order==0.18.2 flake8-bugbear==23.9.16 black"
            )
            return False

    return True


def interactive_mode(use_llm=False):
    """Run in interactive mode to fix files one by one."""
    try:
        # First check if required tools are available
        if not install_missing_tools():
            return 1

        # Add explicit encoding to prevent charmap codec errors
        try:
            flake8_process = subprocess.run(
                [
                    "flake8",
                    "--exclude=venv,.venv,env,.env,virtualenv,__pycache__",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",  # Explicitly use UTF-8 encoding
                errors="replace",  # Replace characters that can't be decoded
            )
        except FileNotFoundError:
            print("\n\033[1;31mError: flake8 command not found.\033[0m")
            print("Make sure flake8 is installed and available in your PATH.")
            print(
                "You can install it with: pip install flake8==6.1.0 "
                "flake8-docstrings==1.7.0 flake8-import-order==0.18.2 "
                "flake8-bugbear==23.9.16"
            )
            return 1

        stdout = flake8_process.stdout

        # Add debugging to check what's being returned
        if not stdout:
            print(
                "No output from flake8. Return code:", flake8_process.returncode
            )
            if flake8_process.stderr:
                print("Error output:", flake8_process.stderr)

        file_issues = count_issues_by_file(stdout)
        if not file_issues:
            # Be more specific here
            if flake8_process.returncode != 0:
                print(
                    "\n\033[1;31mFlake8 encountered an error. See above.\033[0m"
                )
                return 1
            print("\n\033[1;32m✅ All files are already compliant!\033[0m")
            return 0

        # Sort files alphabetically by filename
        sorted_files = sorted(file_issues.items(), key=lambda x: x[0])

        print("\n\033[1;33mFiles sorted alphabetically:\033[0m")
        for i, (_filepath, issues) in enumerate(sorted_files, 1):
            total_issues = sum(issues.values())
            print(f"{i}. {_filepath} - {total_issues} issues")
            # Show top 3 issue types
            top_issues = sorted(
                issues.items(), key=lambda x: x[1], reverse=True
            )[:3]
            for code, count in top_issues:
                print(f"   - {code}: {count} occurrences")

        while True:
            try:
                choice = input("\nEnter file number to fix (q to quit): ")
                if choice.lower() == "q":
                    break

                idx = int(choice) - 1
                if 0 <= idx < len(sorted_files):
                    filepath = sorted_files[idx][0]
                    fix_one_file(filepath, use_llm=use_llm)

                    # Wait for user confirmation before continuing
                    input("\nPress Enter to continue...")

                    # Rerun flake8 to get updated counts - FIX THIS PART
                    flake8_process = subprocess.run(
                        [
                            "flake8",
                            "--exclude=venv,.venv,env,.env,virtualenv,"
                            "__pycache__",
                        ],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",  # Add explicit encoding
                        errors="replace",  # Handle decoding errors
                    )
                    stdout = flake8_process.stdout
                    file_issues = count_issues_by_file(stdout)

                    # Update sorted_files
                    sorted_files = sorted(
                        file_issues.items(),
                        key=lambda x: x[0],  # Sort alphabetically by filename
                    )

                    # Show updated ranking
                    print(
                        "\n\033[1;33m"
                        "Updated files sorted alphabetically:"
                        "\033[0m"
                    )
                    for i, (_filepath, issues) in enumerate(sorted_files, 1):
                        if not issues:  # Skip files with no issues
                            continue
                        total_issues = sum(issues.values())
                        print(f"{i}. {_filepath} - {total_issues} issues")
                else:
                    print("Invalid selection. Try again.")
            except ValueError:
                print("Please enter a valid number.")
            except IndexError:
                print("Selection out of range.")

        return 0

    except Exception as e:
        print(f"\n\033[1;31mAn error occurred: {str(e)}\033[0m")
        # Third-party imports
        import traceback

        traceback.print_exc()
        return 1


def main():
    """Run the code formatting and linting tools."""
    parser = argparse.ArgumentParser(description="Format and lint Python code")
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run in interactive mode to fix files one by one",
    )
    parser.add_argument("-f", "--file", help="Fix a specific file")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check for issues without fixing",
    )
    parser.add_argument(
        "--ai-assist",
        action="store_true",
        help="Use AI to help fix remaining issues",
    )
    parser.add_argument(
        "--configure-llm", action="store_true", help="Configure LLM settings"
    )
    parser.add_argument(
        "--use-config",
        action="store_true",
        help="Use configuration files for formatting tools",
    )
    args = parser.parse_args()

    if args.configure_llm:
        configure_llm()
        return 0

    use_llm = args.ai_assist

    if args.interactive:
        # Check if required tools are available before starting interactive mode
        if not check_tool_exists("flake8") or not check_tool_exists("black"):
            print("\n\033[1;31mRequired tools are missing.\033[0m")
            if not install_missing_tools():
                return 1
        return interactive_mode(use_llm=use_llm)

    if args.file:
        fix_one_file(args.file, use_llm=use_llm)
        return 0

    if args.check:
        # Only run checks without fixing
        black_result, _, _ = run_command(
            [
                "black",
                ".",
                "--check",
                "--exclude",
                r"(\.venv|venv|env|\.env|virtualenv|__pycache__)",
            ],
            "Checking formatting with Black",
        )

        flake8_result, _, _ = run_command(
            ["flake8", "--exclude=venv,.venv,env,.env,virtualenv,__pycache__"],
            "Checking linting with Flake8",
        )

        return 0 if black_result == 0 and flake8_result == 0 else 1

    # Default behavior: Run formatters and show remaining issues
    black_result, _, _ = run_command(
        [
            "black",
            ".",
            "--config=pyproject.toml" if args.use_config else "",
            "--exclude",
            r"(\.venv|venv|env|\.env|virtualenv|__pycache__)",
        ],
        "STEP 1: Running Black to auto-format all Python files",
        capture=False,  # Show real-time output
    )

    try:
        run_command(
            [
                "isort",
                ".",
                "--settings-path=pyproject.toml" if args.use_config else "",
                "--skip",
                "venv",
                "--skip",
                ".venv",
                "--skip",
                "env",
                "--skip",
                ".env",
            ],
            "STEP 2: Running isort to sort imports",
            capture=False,
        )
    except ImportError:
        print("\n\033[1;33mSkipping isort (not installed)\033[0m")

    flake8_result, stdout, _ = run_command(
        ["flake8", "--exclude=venv,.venv,env,.env,virtualenv,__pycache__"],
        "STEP 3: Running Flake8 to identify remaining issues",
    )

    # Summary
    print(
        "\n\033[1;32m===================== SUMMARY ====================\033[0m"
    )
    if black_result == 0:
        print("✅ Black formatting: No issues")
    else:
        print("❌ Black formatting: Issues found")

    if flake8_result == 0:
        print("✅ Flake8 linting: No issues")
    else:
        print("❌ Flake8 linting: Issues found")

        # Provide statistics on errors
        file_issues = count_issues_by_file(stdout)
        print(f"\nIssues found in {len(file_issues)} files")

        # Show most common error types
        error_types = {}
        for _filepath, issues in file_issues.items():
            for code, count in issues.items():
                if code not in error_types:
                    error_types[code] = 0
                error_types[code] += count

        print("\nMost common error types:")
        for code, count in sorted(
            error_types.items(), key=lambda x: x[1], reverse=True
        )[:5]:
            print(f"  - {code}: {count} occurrences")

        print("\nTo fix issues gradually, run with the --interactive flag:")
        print("  python format_code.py --interactive")

    print(
        "\n\033[1;32m=================================================\033[0m"
    )

    return 0 if black_result == 0 and flake8_result == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
