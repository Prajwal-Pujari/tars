import os
import requests
import json
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from dotenv import load_dotenv

load_dotenv()

console = Console()
API_PORT = os.getenv('API_PORT', 8000)
API_HOST = os.getenv('API_HOST', '127.0.0.1')
API_URL = f"http://{API_HOST}:{API_PORT}"
TOKEN = os.getenv("TARS_API_KEY", "tars_secret_key_2024")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def send_chat(message):
    try:
        response = requests.post(
            f"{API_URL}/chat", 
            json={"message": message}, 
            headers=HEADERS,
            timeout=300
        )
        response.raise_for_status()
        return response.json().get("response", "No response content.")
    except requests.exceptions.ConnectionError:
        return "[bold red]Connection Error:[/bold red] Ensure the TARS FastAPI server is running."
    except requests.exceptions.HTTPError as e:
        return f"[bold red]HTTP Error:[/bold red] {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"[bold red]Error communicating with TARS:[/bold red] {e}"

def main():
    console.print(Panel.fit("[bold green]TARS CLI[/bold green]\nSelf-hosted privacy-first AI agent", border_style="green"))
    console.print("Type [bold yellow]'exit'[/bold yellow] or [bold yellow]'quit'[/bold yellow] to leave.\n")
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
            if user_input.lower() in ['exit', 'quit']:
                console.print("[dim]Goodbye.[/dim]")
                break
                
            if not user_input.strip():
                continue
                
            response = send_chat(user_input)
            
            console.print("\n[bold magenta]TARS[/bold magenta]")
            console.print(Markdown(response))
            
        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye.[/dim]")
            break
        except Exception as e:
            console.print(f"[bold red]CLI Error: {e}[/bold red]")

if __name__ == "__main__":
    main()
