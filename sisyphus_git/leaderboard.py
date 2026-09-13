import requests
import sys
from rich.console import Console
from rich.table import Table
from rich import box

def main():
    console = Console()
    
    console.print("\n[bold red]Connecting to the Global Leaderboard of Despair...[/bold red]")
    
    try:
        response = requests.get("http://localhost:8080/leaderboard", timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        console.print(f"[dim]The abyss did not respond. (Error: {e})[/dim]")
        sys.exit(1)
        
    if not data:
        console.print("[dim]The leaderboard is empty. Everyone is suspiciously happy... for now.[/dim]")
        sys.exit(0)
        
    table = Table(
        title="[bold dark_red]THE GLOBAL LEADERBOARD OF DESPAIR[/bold dark_red]", 
        box=box.HEAVY_EDGE, 
        show_header=True, 
        header_style="bold red"
    )
    table.add_column("Rank", justify="right", style="cyan", no_wrap=True)
    table.add_column("Developer", style="magenta")
    table.add_column("Despair Score", justify="right", style="green")
    table.add_column("Commits", justify="right", style="blue")
    table.add_column("Last Words (Commit Message)", style="dim white")
    
    for idx, entry in enumerate(data, start=1):
        table.add_row(
            str(idx),
            entry["username"],
            f"{entry['total_despair']:.2f}",
            str(entry["commits"]),
            entry["latest_message"]
        )
        
    console.print()
    console.print(table)
    console.print()

if __name__ == "__main__":
    main()
