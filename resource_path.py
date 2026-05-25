import os
import sys


def resource_path(relative_path):
    """Resolve asset paths relative to main.py's location, not the working directory."""
    base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, relative_path)
