# LaTeX Debugger

AI-powered LaTeX file debugger using Gemini 3.5 Flash. Fix syntax errors, indentation, spacing, and common warnings without changing your document's content.

[View Patch Notes](PATCHNOTES.md)

## Features

- **Syntax Fixing**: Unmatched braces, missing `$`, environment issues
- **Indentation**: Consistent 2/4 space indentation
- **Spacing**: Fix spacing after commands, remove extra blank lines
- **Warnings**: Fix undefined refs, missing labels, deprecated commands
- **Auto-backup**: Creates `.bak` files before modifications
- **Dry-run mode**: Preview changes without applying

## Quick Start

### Prerequisites

- Python 3.9+
- Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### Installation

```bash
# Clone the repository
git clone https://github.com/thatpedestrian/Latex-debugger.git
cd Latex-debugger

# Install dependencies
pip install -e .
```

### Setup

```bash
# Create .env file with your API key
latex-debug init

# Edit .env and add your GEMINI_API_KEY
```

### Usage

```bash
# Fix all .tex files in current directory
latex-debug

# Preview changes without applying
latex-debug --dry-run

# Fix specific file
latex-debug fix paper.tex

# Show detailed help
latex-debug help-me
```

## Commands

| Command | Description |
|---------|-------------|
| `latex-debug` | Fix all .tex files in current directory |
| `latex-debug fix <file>` | Fix a specific file |
| `latex-debug init` | Create .env file template |
| `latex-debug version` | Show version info |
| `latex-debug help-me` | Show detailed help |

## Flags

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview changes without modifying files |
| `--verbose`, `-v` | Show detailed output |
| `--indent N` | Set indentation size (default: 2) |
| `--pattern GLOB` | File pattern to match (e.g., "*.tex") |
| `--api-key KEY` | Specify API key directly |
| `--restore <file>` | Restore file from .bak backup |
| `--no-interactive` | Skip file selection, fix all files |

## Configuration

Create a `.env` file in your project directory:

```
GEMINI_API_KEY=your_api_key_here
```

## Examples

### Basic usage

```bash
# Navigate to your LaTeX project
cd my-latex-project

# Fix all files
latex-debug
```

### Preview mode

```bash
# See what would change without modifying files
latex-debug --dry-run
```

### Fix specific pattern

```bash
# Fix only chapter files
latex-debug --pattern "chapter*.tex"
```

### Restore from backup

```bash
# Restore original file
latex-debug --restore paper.tex
```

## How It Works

1. Scans your directory for `.tex`, `.sty`, and `.cls` files
2. Sends content to Gemini 3.5 Flash with debugging instructions
3. AI fixes syntax, indentation, spacing, and warnings
4. Creates `.bak` backup of original file
5. Writes fixed content to original file

## Safety Features

- **Auto-backup**: Every modified file gets a `.bak` copy
- **Dry-run mode**: Preview all changes before applying
- **No content changes**: AI only fixes formatting, never changes meaning
- **Restore command**: Easily undo changes from backups

## Troubleshooting

### "No API key found"

Run `latex-debug init` and add your API key to the `.env` file.

### "Rate limit exceeded"

Wait a moment and try again. Gemini API has rate limits.

### "File not found"

Check the file path and make sure you're in the correct directory.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues, please [open an issue](https://github.com/thatpedestrian/Latex-debugger/issues) on GitHub.
