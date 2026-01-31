import os
import sys

# Insert project root (one level up from tests/) to sys.path so top-level packages (like `api`) are importable.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)