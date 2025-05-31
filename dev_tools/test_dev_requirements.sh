# Create another fresh virtual environment
python -m venv test_dev_env

# Activate the environment
# On Windows:
test_dev_env\Scripts\activate

# Install both runtime and development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Test that development tools work
pytest
black . --check
flake8
isort . --check

# If all tools run without errors, your requirements-dev.txt is complete
# Deactivate when done
deactivate
