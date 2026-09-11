import subprocess
import re
from typing import Optional

def get_staged_diff() -> Optional[str]:
    """
    Extracts the staged diff for the commit.
    Returns None if there is no diff, or a truncated string (max 1000 chars) to save tokens.
    """
    try:
        # Run git diff --cached
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=True
        )
        
        diff = result.stdout.strip()
        
        if not diff:
            return None
            
        # Truncate to 1000 characters
        if len(diff) > 1000:
            diff = diff[:1000] + "\n... [diff truncated]"
            
        return diff
    except subprocess.CalledProcessError:
        # If the git command fails (e.g., not in a git repository), return None
        return None
    except FileNotFoundError:
        # Git is not installed
        return None

def get_blame_context() -> str:
    """
    Finds lines being modified in the staged diff, runs git blame on the original file
    to extract authors and timestamps of the surrounding legacy code.
    """
    try:
        diff_output = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, check=True).stdout
        if not diff_output:
            return ""
        
        blame_info = []
        current_file = None
        
        for line in diff_output.split('\n'):
            if line.startswith('--- a/'):
                current_file = line[6:]
            elif line.startswith('@@') and current_file:
                match = re.search(r'@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@', line)
                if match and current_file != '/dev/null':
                    start_line = int(match.group(1))
                    
                    blame_start = max(1, start_line - 2)
                    blame_end = start_line + 5
                    
                    try:
                        blame_result = subprocess.run(
                            ["git", "blame", "-L", f"{blame_start},{blame_end}", "HEAD", "--", current_file],
                            capture_output=True, text=True, check=True
                        )
                        blames = blame_result.stdout.strip()
                        if blames:
                            blame_info.append(f"File: {current_file}\n{blames}")
                    except subprocess.CalledProcessError:
                        pass
                        
        if not blame_info:
            return ""
            
        full_blame = "\\n\\n".join(blame_info)
        if len(full_blame) > 1500:
            full_blame = full_blame[:1500] + "\\n... [blame truncated]"
            
        return "Legacy Code Authorship (Git Blame):\\n" + full_blame
        
    except Exception:
        return ""
