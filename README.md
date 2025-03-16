# cursorrules-tools 🦊

A collection of powerful utilities designed to enhance your experience with Cursor IDE, the AI-powered code editor.

[![GitHub](https://img.shields.io/badge/GitHub-SlyyCooper-blue)](https://github.com/SlyyCooper)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## Overview

This repository contains five specialized tools to help developers get the most out of Cursor IDE by improving AI context, managing ignored files, analyzing dependencies, and more.

## Tools

### 1. `cr` (Cursor Rules)

**Purpose**: Automatically generates and updates `.cursorrules` files to provide better context to Cursor's AI about your project structure.

**Features**:
- Creates a directory tree structure for your project
- Maintains a system prompt in your `.cursorrules` file
- Watches for file system changes to automatically update rules
- Respects `.cursorignore` patterns

**Usage**:
```bash
# Update .cursorrules file once
./cr

# Watch for changes and update automatically
./cr --watch
```

### 2. `ci` (Cursor Ignore)

**Purpose**: Manages `.cursorignore` files to specify which files and directories should be excluded from Cursor's AI analysis.

**Features**:
- Creates `.cursorignore` files with saved patterns
- Maintains a global list of saved patterns
- Adds/removes patterns to/from `.cursorignore`

**Usage**:
```bash
# Create .cursorignore with saved patterns
./ci

# Add a pattern
./ci --add "node_modules"

# Remove a pattern
./ci --remove "node_modules"

# List all saved patterns
./ci --list

# Show help
./ci --help
```

### 3. `codebase`

**Purpose**: Generates comprehensive snapshots of your codebase in a structured format with XML-like tags, providing better context for AI tools.

**Features**:
- Creates a markdown file with your entire codebase structure
- Encapsulates file contents in XML-like tags
- Excludes files based on patterns from `.cursorignore`
- Handles binary files and large files appropriately
- Supports syntax highlighting based on file extensions

**Usage**:
```bash
# Generate a snapshot with default settings
./codebase

# Specify a different directory and output file
./codebase -d /path/to/project -o output.md

# Include markdown files in the snapshot
./codebase -m

# Show verbose output
./codebase -v
```

### 4. `analyze_dependencies`

**Purpose**: Analyzes project dependencies using Claude AI to identify outdated packages and version gaps.

**Features**:
- Finds and analyzes `package.json` and `requirements.txt` files
- Uses Claude 3.7 Sonnet to analyze version information
- Identifies outdated packages and version gaps
- Provides formatted analysis results with markdown
- Can analyze directory structure to provide file descriptions

**Usage**:
```bash
# Analyze dependencies in the current directory
./analyze_dependencies

# The script will automatically find package.json and requirements.txt files
```

### 5. `url-to-md`

**Purpose**: An HTML-to-Markdown converter CLI for creating documentation from web content.

**Features**:
- Fetches HTML content from URLs
- Converts HTML to Markdown with customizable options
- Supports batch processing of multiple URLs
- Generates tables of contents from headings
- Saves both Markdown and optionally raw HTML files

**Usage**:
```bash
# Run the interactive CLI
./url-to-md

# Follow the prompts to:
# - Choose single URL or batch processing
# - Enter URL(s) or file containing URLs
# - Configure conversion options
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SlyyCooper/cursorrules-tools.git
cd cursorrules-tools
```

2. Install required dependencies:
```bash
# For Python scripts
pip install requests questionary html2text rich anthropic

# Make scripts executable
chmod +x ci cr codebase analyze_dependencies url-to-md
```

## Requirements

- Python 3.6+
- Bash shell (for `ci` script)
- Anthropic API key (for `analyze_dependencies`)
- Internet connection (for `url-to-md` and `analyze_dependencies`)

## How These Tools Enhance Cursor IDE

Cursor IDE uses AI to understand your codebase and provide intelligent code suggestions. These tools enhance that experience by:

1. **Providing Better Context**: The `cr` and `codebase` tools give Cursor's AI more information about your project structure.
2. **Focusing AI Analysis**: The `ci` tool helps exclude irrelevant files from analysis.
3. **Maintaining Dependencies**: The `analyze_dependencies` tool helps keep your project dependencies up-to-date.
4. **Improving Documentation**: The `url-to-md` tool helps create Markdown documentation from web content.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Created by [SlyyCooper](https://github.com/SlyyCooper) 🦊
 
