import sys
import os
import time
from rich.console import Console

from sisyphus_git.git_tools import get_staged_diff
from sisyphus_git.ai_philosopher import AIPhilosopher
from sisyphus_git.sentiment_gate import SentimentGate
from sisyphus_git.sabotage import Saboteur

def setup_tty():
    """
    Attempts to re-route stdin to the TTY.
    This is necessary because git hooks run without a terminal attached to stdin.
    """
    try:
        # Standard Unix / Git Bash environment
        sys.stdin = open('/dev/tty', 'r')
    except FileNotFoundError:
        try:
            # Fallback for standard Windows command prompt
            sys.stdin = open('CON', 'r')
        except FileNotFoundError:
            print("Warning: Could not bind to TTY. Interactive prompts may fail.", file=sys.stderr)

def typewriter_print(text: str, console: Console):
    """Prints text with a typewriter effect in bold red."""
    for char in text:
        console.print(f"[bold red]{char}[/bold red]", end="")
        sys.stdout.flush()
        # Sleep for a tiny amount to simulate typing
        time.sleep(0.02)
    console.print() # Newline at the end

def main():
    console = Console()
    
    # Re-route stdin
    setup_tty()
    
    console.clear()
    console.print("[dim][Sisyphus-Git] Analyzing commit...[/dim]")
    
    diff = get_staged_diff()
    
    if not diff:
        console.print("[dim]No diff detected. The void remains undisturbed.[/dim]")
        sys.exit(0)
        
    try:
        philosopher = AIPhilosopher()
        gate = SentimentGate()
        saboteur = Saboteur()
    except Exception as e:
        console.print(f"[bold red]System Error: {e}[/bold red]")
        sys.exit(1)
        
    chat_history = []
    
    try:
        while True:
            # Fetch response from AI
            insult = philosopher.get_insult(diff, chat_history)
            
            # Print with typewriter effect
            console.print("\n")
            typewriter_print(insult, console)
            console.print("\n")
            
            # Prompt user
            user_input = input("[You]: ").strip()
            
            if not user_input:
                continue
                
            # Check if the user explained their change scientifically / mathematically
            passes_gate, score = gate.check_despair(user_input)
            if passes_gate:
                saboteur.record_success()
                console.print("\n[dim]Scientific justification accepted. The boulder may roll... for now.[/dim]")
                
                # POST to leaderboard
                try:
                    import subprocess
                    import requests
                    
                    # Get git username
                    user_name_proc = subprocess.run(
                        ["git", "config", "user.name"], 
                        capture_output=True, text=True, check=True
                    )
                    username = user_name_proc.stdout.strip() or "Anonymous Sisyphus"
                    
                    console.print(f"[dim]Uploading despair for {username}...[/dim]")
                    
                    # Read backend URL from env (set SISYPHUS_BACKEND_URL in .env for production)
                    backend_url = os.environ.get("SISYPHUS_BACKEND_URL", "http://localhost:8000")
                    requests.post(f"{backend_url}/score", json={
                        "username": username,
                        "despair_score": score,
                        "commit_message": user_input
                    }, timeout=2)
                    
                except Exception as e:
                    console.print(f"[dim]Failed to reach the Global Leaderboard of Despair. Your misery remains local. ({e})[/dim]")
                
                sys.exit(0)
            
            # Failed the science gate — mock the user and continue the loop
            console.print("\n[bold red]Sisyphus scoffs: That was not science. That was poetry at best. Explain yourself MATHEMATICALLY.[/bold red]")
            punishment_msg = saboteur.record_failure()
            if punishment_msg:
                console.print(f"\n[bold red]{punishment_msg}[/bold red]")
                sys.exit(1)
                
            # Otherwise, add to history and continue loop
            chat_history.append({"role": "assistant", "content": insult})
            chat_history.append({"role": "user", "content": user_input})
            
    except KeyboardInterrupt:
        console.print("\n\n[bold red]Cowardice detected. Commit aborted.[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
