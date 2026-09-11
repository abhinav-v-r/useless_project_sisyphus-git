import subprocess

def get_staged_diff() -> str | None:
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
