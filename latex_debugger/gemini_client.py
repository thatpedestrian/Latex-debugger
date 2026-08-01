"""Gemini API client for LaTeX debugging."""

import os
from google import genai
from google.genai import types


class GeminiClient:
    """Wrapper for Gemini 3.5 Flash API."""

    SYSTEM_PROMPT = """You are a LaTeX debugging assistant. Your task is to fix LaTeX code issues WITHOUT changing the document's content, meaning, or structure.

Fix ONLY the following issues:
- Syntax errors (unmatched braces, missing $, incorrect environment nesting)
- Indentation consistency (use 2 spaces by default)
- Spacing issues (extra spaces, missing spaces after commands)
- Common warnings (undefined references, missing labels, deprecated commands)
- Bracket and environment matching
- Comment formatting

RULES:
1. Return ONLY the fixed LaTeX code - no explanations, no markdown code blocks
2. Do NOT add or remove any content
3. Do NOT change the document structure or meaning
4. Do NOT modify text content, only formatting and syntax
5. Preserve all comments
6. Keep the original encoding and line endings"""

    def __init__(self, api_key: str = None):
        """Initialize the Gemini client.

        Args:
            api_key: Gemini API key. If not provided, reads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key provided. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.client = genai.Client(api_key=self.api_key)

    def fix_latex(self, content: str, filename: str = "untitled.tex") -> str:
        """Send LaTeX content to Gemini for debugging.

        Args:
            content: The LaTeX source code to fix.
            filename: Name of the file (for context).

        Returns:
            Fixed LaTeX source code.
        """
        user_message = f"Fix the LaTeX code in {filename}:\n\n{content}"

        response = self.client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=self.SYSTEM_PROMPT),
                        types.Part.from_text(text=user_message),
                    ],
                )
            ],
        )

        result = response.text

        # Strip markdown code block formatting if present
        if result.startswith("```latex"):
            result = result[8:]
        elif result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]

        return result.strip()
