import sys
import os

print("Current file directory:", os.path.dirname(__file__))
print("Parent directory:", os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("sys.path:", sys.path)

try:
    from main import app
    print("Import successful")
except ModuleNotFoundError as e:
    print("ModuleNotFoundError:", e)
