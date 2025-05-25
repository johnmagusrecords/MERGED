"""
unused_helpers – stub utilities for stats and HTML templates.
"""

import os
import pandas as pd


def get_stats(data):
    """Return a dict with the count of items in data if possible."""
    if hasattr(data, '__len__'):
        return {"count": len(data)}
    return {"count": 0}


def load_html_template(name: str) -> str:
    """Return a minimal HTML snippet with the template name."""
    return f"<html><body>Template: {name}</body></html>"


def list_directory_files(directory):
    """List all files in a directory using os module."""
    return os.listdir(directory)


def create_sample_dataframe():
    """Create a sample DataFrame using pandas."""
    data = {
        "Column1": [1, 2, 3],
        "Column2": ["A", "B", "C"]
    }
    return pd.DataFrame(data)