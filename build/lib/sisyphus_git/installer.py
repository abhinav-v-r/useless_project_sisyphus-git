import os
import sys
from pathlib import Path
from typing import Optional

def get_git_hooks_dir() -> Optional[Path]:
    """Finds the .git/hooks/ directory in the current or parent directories."""
    current_dir = Path.cwd()
    while True:
        git_dir = current_dir / ".git"
        if git_dir.is_dir():
            hooks_dir = git_dir / "hooks"
            hooks_dir.mkdir(exist_ok=True)
            return hooks_dir
        
        parent = current_dir.parent
        if parent == current_dir:
            return None
        current_dir = parent

def main():
    print("Installing Sisyphus-Git hook...")
    hooks_dir = get_git_hooks_dir()
    
    if not hooks_dir:
        print("Error: Could not find .git directory. Are you in a git repository?", file=sys.stderr)
        sys.exit(1)
        
    hook_path = hooks_dir / "pre-commit"
    
    # The bash script required to run sisyphus-run with TTY hijacking
    hook_script = """#!/bin/bash
# Sisyphus-Git Pre-Commit Hook

# Re-route stdin to the TTY so we can prompt the user
exec < /dev/tty

# Execute the main program
sisyphus-run
"""
    
    try:
        with open(hook_path, "w", newline="\n") as f:
            f.write(hook_script)
            
        # Make the hook executable (equivalent to chmod +x)
        # On Windows this might not be strictly necessary for git bash, but it's good practice
        hook_path.chmod(hook_path.stat().st_mode | 0o111)
        
        print(f"Successfully installed Sisyphus-Git hook at {hook_path}")
        print("May your commits be forever pointless.")
        
    except Exception as e:
        print(f"Error installing hook: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
