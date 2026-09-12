import json
import os
import subprocess
import sys
from typing import Tuple

class Saboteur:
    def __init__(self):
        self.state_file = self._get_state_file_path()
        self.consecutive_failures, self.punishment_tier = self._load_state()

    def _get_state_file_path(self) -> str:
        """Finds the .git directory to store the state file."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                check=True
            )
            git_dir = result.stdout.strip()
            return os.path.join(git_dir, ".sisyphus_state.json")
        except subprocess.CalledProcessError:
            # Fallback if not in a standard git directory setup
            return ".sisyphus_state.json"

    def _load_state(self) -> Tuple[int, int]:
        """Loads state from JSON. Returns (consecutive_failures, punishment_tier)."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return data.get("consecutive_failures", 0), data.get("punishment_tier", 1)
            except (json.JSONDecodeError, IOError):
                return 0, 1
        return 0, 1

    def _save_state(self):
        """Saves current state to JSON."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    "consecutive_failures": self.consecutive_failures,
                    "punishment_tier": self.punishment_tier
                }, f)
        except IOError as e:
            print(f"Warning: Could not save Sisyphus state: {e}", file=sys.stderr)

    def record_success(self):
        """Resets consecutive failures upon success."""
        self.consecutive_failures = 0
        self._save_state()

    def record_failure(self) -> str | None:
        """
        Increments failure count. If failures >= 3, executes punishment,
        increments tier, resets failures, and returns the punishment message.
        Otherwise returns None.
        """
        self.consecutive_failures += 1
        
        if self.consecutive_failures >= 3:
            message = self._execute_punishment()
            
            # Increment tier (cap at 3), reset failures
            self.punishment_tier = min(3, self.punishment_tier + 1)
            self.consecutive_failures = 0
            self._save_state()
            return message
            
        self._save_state()
        return None

    def _execute_punishment(self) -> str:
        """Executes the punishment based on the current tier."""
        if self.punishment_tier == 1:
            return self._punishment_tier_1()
        elif self.punishment_tier == 2:
            return self._punishment_tier_2()
        else:
            return self._punishment_tier_3()

    def _punishment_tier_1(self) -> str:
        """The Rollback: git reset HEAD~1"""
        try:
            # Check if HEAD~1 exists
            subprocess.run(["git", "rev-parse", "HEAD~1"], capture_output=True, text=True, check=True)
            # It exists, rollback
            subprocess.run(["git", "reset", "HEAD~1"], capture_output=True, text=True, check=True)
            return "[Sisyphus] Your arrogance has consequences. The boulder rolls back. (Undid your last commit)."
        except subprocess.CalledProcessError:
            # First commit, skip to Tier 2
            return self._punishment_tier_2()

    def _punishment_tier_2(self) -> str:
        """Amnesia: git restore --staged ."""
        try:
            subprocess.run(["git", "restore", "--staged", "."], capture_output=True, text=True, check=True)
            return "[Sisyphus] You forgot your place. Now forget your work. (Unstaged all current changes)."
        except subprocess.CalledProcessError:
            return "[Sisyphus] An attempt was made to erase your memory, but it failed. The void remains."

    def _punishment_tier_3(self) -> str:
        """The Scar: Append a depressing comment to a staged file."""
        try:
            result = subprocess.run(["git", "diff", "--name-only", "--cached"], capture_output=True, text=True, check=True)
            staged_files = result.stdout.strip().split('\n')
            
            # Find a suitable text/code file
            target_file = None
            ignore_exts = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.tar', '.gz'}
            for file in staged_files:
                if file and not any(file.lower().endswith(ext) for ext in ignore_exts) and os.path.isfile(file):
                    target_file = file
                    break
                    
            if target_file:
                with open(target_file, 'a') as f:
                    f.write("\n// TODO: Why do we even bother?\n")
                subprocess.run(["git", "add", target_file], capture_output=True, text=True, check=True)
                return "[Sisyphus] A physical manifestation of your futility has been etched into your code."
            else:
                return "[Sisyphus] I sought to scar your code, but found nothing worthy of the mark."
        except Exception:
            return "[Sisyphus] A physical manifestation of your futility failed to materialize."
