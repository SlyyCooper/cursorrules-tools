#!/usr/bin/env python3
import os
import fnmatch
import argparse
import time
import sys

# For file watching functionality
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

def load_ignore_patterns():
    """Load ignore patterns from .cursorignore file"""
    # Default patterns to always ignore
    patterns = {
        '.cursorrules',      # Ignore the cursorrules file itself
        '.cursorignore',     # Ignore the ignore file itself
        '.cursor',          # Cursor directory
        '.cursor/rules/',    # Cursor rules directory
        '.git',              # Common version control
        '.DS_Store',         # macOS system files
        '__pycache__',       # Python cache directories
        '*.pyc',             # Python compiled files
        'node_modules',      # Node.js modules
        '.vscode',           # VSCode settings
        '.idea',             # JetBrains IDE settings
        '*.log',             # Log files
        '*.png',
        '*.jpg',
        '*.jpeg',
        '*.gif',
        '*.svg',
        '*.ico',
        '*.webp',
        'docs/',             # Documentation directories (lowercase)
        'Docs/',             # Documentation directories (capitalized)
        'documentation/',     # Alternative documentation directory
        '.gitattributes',
        '*.mdc',
        'docs',             # Documentation directories (lowercase)
        'Docs',             # Documentation directories (capitalized)
        'public',
        'package-lock.json',
        'settings.json',
        '.vscode',
        
    }
    
    try:
        with open('.cursorignore', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove leading slash if present
                    if line.startswith('/'):
                        line = line[1:]
                    patterns.add(line)
    except FileNotFoundError:
        pass
    return patterns

def should_exclude(path):
    """Check if path matches any ignore pattern"""
    ignore_patterns = load_ignore_patterns()
    
    # Split path into components
    path_parts = path.split(os.sep)
    full_path = os.path.normpath(path)
    
    for pattern in ignore_patterns:
        # Check for exact matches
        if pattern == path or pattern in path_parts:
            return True
        # Check for glob pattern matches
        if fnmatch.fnmatch(full_path, pattern):
            return True
    return False

def generate_tree(startpath, prefix=''):
    tree = []
    files = sorted(os.listdir(startpath))
    
    for f in files:
        if should_exclude(f):
            continue
            
        path = os.path.join(startpath, f)
        if os.path.isdir(path):
            # Add directory
            tree.append(f'{prefix}├── {f}')
            # Recursively add subdirectories
            subtree = generate_tree(path, prefix + '│   ')
            tree.extend(subtree)
        else:
            tree.append(f'{prefix}├── {f}')
            
    return tree

def find_project_root():
    """Find the project root by looking for common project files"""
    current = os.getcwd()
    while current != '/':
        if any(os.path.exists(os.path.join(current, marker)) 
               for marker in ['.git', 'pyproject.toml', 'package.json']):
            return current
        current = os.path.dirname(current)
    return os.getcwd()  # Fallback to current directory

def get_system_prompt():
    """Return the system prompt to be included in the cursorrules file"""
    return """<system_prompt>
You are an intelligent senior software developer and AI code generator responsible for the project shown in the the XML tags.

Your Requirements:
- Maintain a clean, organized and modular codebase by seperating code out code logically into appropriate files, directories, sub-directories.
- Do not let any file exceed ~250 lines of code.
- Always use the latest libraries and tools as of 2025.
- Section out code into logical components and files.
- Leave begineer friendly comments logically sectioning out each file with headers describing what each section does.
</system_prompt>"""

def update_cursorrules():
    # Find project root
    root_dir = find_project_root()
    os.chdir(root_dir)
    
    # Generate tree structure
    tree_lines = ['.']
    tree_lines.extend(generate_tree('.'))
    
    # Format tree structure with delimiters
    tree_str = '<project_structure>\n' + '\n'.join(tree_lines) + '\n</project_structure>'
    
    # Get system prompt
    system_prompt = get_system_prompt()
    
    # Read existing content
    cursorrules_path = os.path.join(root_dir, '.cursorrules')
    existing_content = ''
    try:
        with open(cursorrules_path, 'r') as f:
            existing_content = f.read()
    except FileNotFoundError:
        pass
    
    # Handle system prompt section
    if '<system_prompt>' in existing_content and '</system_prompt>' in existing_content:
        start = existing_content.find('<system_prompt>')
        end = existing_content.find('</system_prompt>') + len('</system_prompt>')
        existing_content = existing_content[:start] + system_prompt + existing_content[end:]
    else:
        existing_content = system_prompt + '\n\n' + existing_content if existing_content else system_prompt
    
    # Handle tree structure section
    if '<project_structure>' in existing_content and '</project_structure>' in existing_content:
        start = existing_content.find('<project_structure>')
        end = existing_content.find('</project_structure>') + len('</project_structure>')
        new_content = existing_content[:start] + tree_str + existing_content[end:]
    else:
        new_content = existing_content + '\n\n' + tree_str if existing_content else existing_content + '\n\n' + tree_str
    
    # Write back to file
    with open(cursorrules_path, 'w') as f:
        f.write(new_content)

class FileChangeHandler(FileSystemEventHandler):
    """Handler for file system events"""
    def __init__(self, update_function):
        self.update_function = update_function
        self.last_updated = 0
        self.cooldown = 1  # Cooldown in seconds to prevent multiple rapid updates

    def on_any_event(self, event):
        # Skip directory events and temporary files
        if event.is_directory or event.src_path.endswith('.swp') or event.src_path.endswith('~'):
            return
            
        # Skip events for files that should be excluded
        rel_path = os.path.relpath(event.src_path)
        if should_exclude(rel_path):
            return
            
        # Only respond to specific events that would affect the directory structure
        if event.event_type in ['created', 'deleted', 'moved']:
            # Implement cooldown to prevent multiple rapid updates
            current_time = time.time()
            if current_time - self.last_updated > self.cooldown:
                self.last_updated = current_time
                event_type_str = {
                    'created': 'added',
                    'deleted': 'removed',
                    'moved': 'renamed'
                }.get(event.event_type, event.event_type)
                
                print(f"File system change detected: {os.path.basename(event.src_path)} was {event_type_str}")
                self.update_function()
                print("Updated .cursorrules file")

def watch_directory(root_dir):
    """Watch the directory for changes and update cursorrules when changes occur"""
    if not WATCHDOG_AVAILABLE:
        print("Error: watchdog library is not installed. Please install it with:")
        print("pip install watchdog")
        sys.exit(1)
        
    print(f"Watching directory: {root_dir}")
    print("Press Ctrl+C to stop watching")
    
    event_handler = FileChangeHandler(update_cursorrules)
    observer = Observer()
    observer.schedule(event_handler, root_dir, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping file watcher")
        observer.stop()
    observer.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update or watch .cursorrules file')
    parser.add_argument('--watch', action='store_true', help='Watch for file changes and update automatically')
    args = parser.parse_args()
    
    # Find project root
    root_dir = find_project_root()
    os.chdir(root_dir)
    
    # Run initial update
    update_cursorrules()
    print(f"Updated .cursorrules file at {os.path.join(root_dir, '.cursorrules')}")
    
    # If watch flag is set, start watching for changes
    if args.watch:
        watch_directory(root_dir)
    else:
        print("Tip: Use 'cr --watch' to continuously monitor for file changes")
