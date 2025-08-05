```bash
# Install flake8 and useful plugins
pip install flake8 flake8-docstrings flake8-import-order flake8-bugbear black

# You may want to add them to your requirements-dev.txt
echo "flake8==6.1.0" >> requirements-dev.txt
echo "flake8-docstrings==1.7.0" >> requirements-dev.txt
echo "flake8-import-order==0.18.2" >> requirements-dev.txt
echo "flake8-bugbear==23.9.16" >> requirements-dev.txt
echo "black==23.9.1" >> requirements-dev.txt

# Install pre-commit
pip install pre-commit

# Add pre-commit to requirements-dev.txt
echo "pre-commit==3.4.0" >> requirements-dev.txt

# Initialize pre-commit in your repository
cd c:\Users\mjhug\Documents\GitHub\scanner-controller
pre-commit install

# Format all Python files with black
black .

# Run flake8 check
flake8

# Specific issues to fix in your BC125AT adapter:
# 1. Rename camelCase methods to snake_case (get_help instead of getHelp)
# 2. Fix docstrings that don't match implementation
# 3. Ensure line length doesn't exceed limits
```
