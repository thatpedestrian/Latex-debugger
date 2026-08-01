# Patch Notes

All notable changes to LaTeX Debugger will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] - 2026-08-01

### Changed

- Removed ASCII art logo from CLI and README for cleaner interface

---

## [1.1.0] - 2026-08-01

### Added

- **Interactive file selection**: When multiple .tex files are found, users can now select which files to fix
- **Loading spinner with elapsed time**: Shows a spinner animation and elapsed time while processing files
- **--no-interactive flag**: Skip file selection and fix all files automatically

### Improved

- Better user experience with visual feedback during file processing
- Enhanced CLI help text with new flag documentation

---

## [1.0.0] - 2026-08-01

### Added

- **Initial release** of LaTeX Debugger
- AI-powered LaTeX file fixing using Gemini 3.5 Flash
- Automatic detection of `.tex`, `.sty`, and `.cls` files
- Syntax error fixing (unmatched braces, missing `$`, environment issues)
- Indentation consistency enforcement
- Spacing normalization
- Common warning fixes (undefined refs, missing labels)
- Auto-backup system with `.bak` file creation
- Dry-run mode for previewing changes
- Verbose output mode
- Configurable indentation size
- File pattern matching support
- Restore from backup functionality
- Interactive help system with `help-me` command
- Environment variable and `.env` file support for API key
- Rich terminal output with colors and formatting
- Cross-platform compatibility (Windows, macOS, Linux)

### Technical Details

- Built with Python 3.9+
- Uses Click for CLI framework
- Integrates Google GenAI SDK for Gemini 3.5 Flash
- Rich library for terminal formatting
- python-dotenv for environment variable management

---

## [Upcoming]

### Planned Features

- [ ] Interactive mode with confirmation prompts
- [ ] Undo/redo functionality
- [ ] Custom prompt templates
- [ ] Batch processing with progress bars
- [ ] LaTeX compilation error detection
- [ ] Support for `.bib` files
- [ ] Git integration (auto-commit after fixes)
- [ ] Configuration file support
- [ ] Plugin system for custom rules
- [ ] Multi-language support

### Known Issues

- None reported yet

---

*Last updated: August 1, 2026*
