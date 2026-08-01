"""Core LaTeX debugging logic."""

import os
import shutil
import sys
import time
import threading
from pathlib import Path
from typing import List, Optional, Tuple

from .gemini_client import GeminiClient


class Spinner:
    """A loading spinner with elapsed time."""

    def __init__(self, message: str = "Processing"):
        self.message = message
        self.spinner_chars = ["|", "/", "-", "\\"]
        self.index = 0
        self.running = False
        self.thread = None
        self.start_time = None

    def _spin(self):
        while self.running:
            elapsed = time.time() - self.start_time
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            sys.stdout.write(
                f"\r  {self.spinner_chars[self.index % len(self.spinner_chars)]} {self.message}... [{mins:02d}:{secs:02d}]"
            )
            sys.stdout.flush()
            self.index += 1
            time.sleep(0.1)

    def start(self):
        self.start_time = time.time()
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()

    def stop(self, final_message: str = None):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.2)
        elapsed = time.time() - self.start_time
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        if final_message:
            sys.stdout.write(f"\r  {final_message} [{mins:02d}:{secs:02d}]\n")
        else:
            sys.stdout.write(f"\r  Done [{mins:02d}:{secs:02d}]          \n")
        sys.stdout.flush()


class LatexDebugger:
    """Main debugger class for processing LaTeX files."""

    DEFAULT_EXTENSIONS = (".tex", ".sty", ".cls")

    def __init__(
        self,
        api_key: str = None,
        indent_size: int = 2,
        dry_run: bool = False,
        verbose: bool = False,
    ):
        """Initialize the debugger.

        Args:
            api_key: Gemini API key.
            indent_size: Number of spaces for indentation.
            dry_run: If True, don't actually write changes.
            verbose: If True, print detailed output.
        """
        self.client = GeminiClient(api_key)
        self.indent_size = indent_size
        self.dry_run = dry_run
        self.verbose = verbose
        self.changes_made = []
        self.errors = []

    def find_tex_files(
        self, directory: str = ".", pattern: str = None
    ) -> List[Path]:
        """Find all LaTeX files in directory.

        Args:
            directory: Directory to search.
            pattern: Optional glob pattern (e.g., "*.tex").

        Returns:
            List of Path objects for found files.
        """
        dir_path = Path(directory)
        if pattern:
            files = list(dir_path.glob(pattern))
        else:
            files = []
            for ext in self.DEFAULT_EXTENSIONS:
                files.extend(dir_path.glob(f"*{ext}"))

        # Filter out backup files and aux files
        files = [f for f in files if not f.suffix == ".bak"]
        files = [f for f in files if not f.name.startswith(".")]

        return sorted(files)

    def create_backup(self, file_path: Path) -> Path:
        """Create a backup of the file.

        Args:
            file_path: Path to the file to backup.

        Returns:
            Path to the backup file.
        """
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        shutil.copy2(file_path, backup_path)
        if self.verbose:
            print(f"  Backup created: {backup_path.name}")
        return backup_path

    def restore_backup(self, file_path: Path) -> bool:
        """Restore a file from its backup.

        Args:
            file_path: Path to the original file.

        Returns:
            True if restored successfully, False otherwise.
        """
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        if backup_path.exists():
            shutil.copy2(backup_path, file_path)
            return True
        return False

    def read_file(self, file_path: Path) -> str:
        """Read a file's content.

        Args:
            file_path: Path to read.

        Returns:
            File content as string.
        """
        # Try different encodings
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Could not read {file_path} with any supported encoding")

    def fix_file(self, file_path: Path) -> Tuple[bool, str]:
        """Fix a single LaTeX file.

        Args:
            file_path: Path to the file to fix.

        Returns:
            Tuple of (success, message).
        """
        try:
            if self.verbose:
                print(f"\nProcessing: {file_path.name}")

            # Read original content
            original = self.read_file(file_path)

            if not original.strip():
                return True, "File is empty, skipping"

            # Get fixed content from Gemini
            fixed = self.client.fix_latex(original, file_path.name)

            # Compare content
            if original == fixed:
                if self.verbose:
                    print(f"  No changes needed")
                return True, "No changes needed"

            # Calculate changes
            changes = self._count_changes(original, fixed)

            if self.dry_run:
                self._show_diff(file_path, original, fixed)
                return True, f"Would make {changes} change(s) (dry run)"

            # Create backup and write
            self.create_backup(file_path)
            file_path.write_text(fixed, encoding="utf-8")

            self.changes_made.append(
                {"file": str(file_path), "changes": changes}
            )

            return True, f"Fixed {changes} change(s)"

        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {str(e)}"
            self.errors.append(error_msg)
            return False, error_msg

    def _count_changes(self, original: str, fixed: str) -> int:
        """Count approximate number of changes."""
        orig_lines = original.splitlines()
        fixed_lines = fixed.splitlines()
        changes = abs(len(orig_lines) - len(fixed_lines))

        for i, (o, f) in enumerate(zip(orig_lines, fixed_lines)):
            if o != f:
                changes += 1

        return changes

    def _show_diff(self, file_path: Path, original: str, fixed: str):
        """Show a simple diff of changes."""
        print(f"\n--- Changes for {file_path.name} ---")

        orig_lines = original.splitlines()
        fixed_lines = fixed.splitlines()

        max_lines = max(len(orig_lines), len(fixed_lines))

        for i in range(max_lines):
            orig = orig_lines[i] if i < len(orig_lines) else None
            fixed = fixed_lines[i] if i < len(fixed_lines) else None

            if orig != fixed:
                if orig is not None:
                    print(f"  - Line {i+1}: {orig[:80]}...")
                if fixed is not None:
                    print(f"  + Line {i+1}: {fixed[:80]}...")

    def select_files(self, files: List[Path]) -> List[Path]:
        """Let user select which files to fix when multiple are found.

        Args:
            files: List of found files.

        Returns:
            List of selected files.
        """
        if len(files) == 0:
            return []
        
        if len(files) == 1:
            return files

        print(f"\nFound {len(files)} LaTeX file(s):\n")
        for i, f in enumerate(files, 1):
            size = f.stat().st_size
            size_str = self._format_size(size)
            print(f"  [{i}] {f.name} ({size_str})")

        print(f"\n  [A] Fix all files")

        while True:
            try:
                choice = input("\nSelect file(s) to fix (e.g., 1,2,3 or A): ").strip().upper()
                
                if choice == 'A':
                    return files
                
                # Parse comma-separated numbers
                indices = [int(x.strip()) for x in choice.split(',')]
                
                # Validate indices
                selected = []
                for idx in indices:
                    if 1 <= idx <= len(files):
                        selected.append(files[idx - 1])
                    else:
                        print(f"  Invalid selection: {idx}")
                        continue
                
                if selected:
                    return selected
                else:
                    print("  No valid files selected. Try again.")
                    
            except ValueError:
                print("  Invalid input. Use numbers separated by commas (e.g., 1,2,3) or 'A' for all.")
            except KeyboardInterrupt:
                print("\n\nCancelled.")
                return []

    def _format_size(self, size_bytes: int) -> str:
        """Format byte size to human readable string."""
        for unit in ["B", "KB", "MB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} GB"

    def fix_directory(
        self, directory: str = ".", pattern: str = None, interactive: bool = True
    ) -> dict:
        """Fix all LaTeX files in a directory.

        Args:
            directory: Directory to process.
            pattern: Optional glob pattern.
            interactive: If True and multiple files, ask user to select.

        Returns:
            Dictionary with results summary.
        """
        files = self.find_tex_files(directory, pattern)

        if not files:
            return {
                "success": True,
                "files_found": 0,
                "files_fixed": 0,
                "message": "No LaTeX files found",
            }

        # Let user select files if interactive and multiple found
        if interactive and len(files) > 1:
            files = self.select_files(files)
            if not files:
                return {
                    "success": True,
                    "files_found": 0,
                    "files_fixed": 0,
                    "message": "No files selected",
                }

        print(f"\nProcessing {len(files)} file(s)...\n")

        files_fixed = 0
        for file_path in files:
            spinner = Spinner(f"Fixing {file_path.name}")
            spinner.start()
            
            success, message = self.fix_file(file_path)
            
            if success and "Fixed" in message:
                files_fixed += 1
                spinner.stop(f"Fixed {file_path.name}")
            elif "No changes" in message:
                spinner.stop(f"No changes needed for {file_path.name}")
            else:
                spinner.stop(f"Error: {file_path.name}")
            
            print(f"    {message}")

        # Summary
        summary = {
            "success": len(self.errors) == 0,
            "files_found": len(files),
            "files_fixed": files_fixed,
            "changes": self.changes_made,
            "errors": self.errors,
        }

        return summary

    def print_summary(self):
        """Print a summary of all changes made."""
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)

        if self.dry_run:
            print("Mode: DRY RUN (no files were modified)")

        if self.changes_made:
            print(f"\nFiles modified: {len(self.changes_made)}")
            for change in self.changes_made:
                print(f"  - {change['file']}: {change['changes']} change(s)")

        if self.errors:
            print(f"\nErrors: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")

        if not self.changes_made and not self.errors:
            print("\nNo changes needed - all files look good!")

        print("=" * 50)
