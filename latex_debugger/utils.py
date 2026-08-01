"""Utility functions for LaTeX Debugger."""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_api_key() -> str:
    """Load Gemini API key from .env file or environment.

    Returns:
        API key string or empty string if not found.
    """
    # Try loading from current directory
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
        if os.getenv("GEMINI_API_KEY"):
            return os.getenv("GEMINI_API_KEY")

    # Try loading from package directory as fallback
    package_dir = Path(__file__).parent.parent
    env_path = package_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        if os.getenv("GEMINI_API_KEY"):
            return os.getenv("GEMINI_API_KEY")

    # Try user home directory
    home_env = Path.home() / ".latex-debugger.env"
    if home_env.exists():
        load_dotenv(home_env)
        if os.getenv("GEMINI_API_KEY"):
            return os.getenv("GEMINI_API_KEY")

    return os.getenv("GEMINI_API_KEY", "")


def validate_api_key(api_key: str) -> bool:
    """Validate that an API key is present.

    Args:
        api_key: The API key to validate.

    Returns:
        True if key appears valid, False otherwise.
    """
    if not api_key:
        return False
    # Basic validation - Gemini keys typically start with specific patterns
    return len(api_key) > 10


def get_file_encoding(file_path: Path) -> str:
    """Detect file encoding.

    Args:
        file_path: Path to the file.

    Returns:
        Encoding string.
    """
    encodings = ["utf-8", "latin-1", "cp1252", "ascii"]

    for encoding in encodings:
        try:
            with open(file_path, encoding=encoding) as f:
                f.read()
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue

    return "utf-8"  # Default fallback


def format_size(size_bytes: int) -> str:
    """Format byte size to human readable string.

    Args:
        size_bytes: Size in bytes.

    Returns:
        Formatted string (e.g., "1.5 KB").
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def print_colored(text: str, color: str = "white"):
    """Print colored text to terminal.

    Args:
        text: Text to print.
        color: Color name (red, green, yellow, blue, white).
    """
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "white": "\033[97m",
        "reset": "\033[0m",
    }

    color_code = colors.get(color, colors["white"])
    reset_code = colors["reset"]
    print(f"{color_code}{text}{reset_code}")
