# Create a fresh virtual environment
python -m venv test_env

# Activate the environment
# On Unix/macOS:
source test_env/bin/activate
# On Windows use:
test_env\Scripts\activate

# Install only runtime dependencies
pip install -r requirements.txt

# Try to run your application
# Replace main.py with your actual entry point
python main.py

# If no import errors occur, your requirements.txt is complete
# Deactivate when done
deactivate
