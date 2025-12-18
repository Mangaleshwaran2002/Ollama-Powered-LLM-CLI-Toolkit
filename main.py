import sys
import ollama
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.table import Table
from rich.padding import Padding
from rich.prompt import Prompt
from typing import Generator, List, Optional
# Initialize the rich console
console = Console()

class LLM:
    """Simple wrapper that lets you pick a local Ollama model and chat with it."""

    def __init__(self) -> None:
        self.model: Optional[str] = None

    # --------------------------------------------------------------------- #
    # Helper – unified error handling for Ollama calls
    # --------------------------------------------------------------------- #
    @staticmethod
    def _handle_ollama_error(exc: Exception) -> None:
        """Print a friendly message and exit."""
        console.print(f"[bold red]Ollama error:[/bold red] {exc}")
        console.print(
            "[bold yellow]Make sure the Ollama daemon is running and the model exists.[/bold yellow]"
        )
        sys.exit(1)

    # --------------------------------------------------------------------- #
    # Model management helpers
    # --------------------------------------------------------------------- #
    
    def download_model(self) -> None:
        """function to download model using model tag."""
        console.rule("[bold red]Download model")
        with console.screen(style="bold white on red") as screen: 
            model_tag=Prompt.ask(prompt="Enter model tag (e.g: gemma3:1b): ",default="gemma3:1b")
            screen.console.print(f"model tag : {model_tag}")
            with Progress(
                TextColumn("[bold blue]{task.description}", justify="right"),
                BarColumn(bar_width=50),
                "[progress.percentage]{task.percentage:>1.1f}%",
                "•",
                DownloadColumn(),
                "•",
                TransferSpeedColumn(),
                "•",
                TimeRemainingColumn(),
                console=console,
                transient=True # Optional: removes the bar from the terminal when finished
            ) as progress:
                # We start the progress display within a context manager, which handles start() and stop() automatically.
                screen.console.print(f"Starting download of {model_tag}")
                # We don't know the total size immediately, so we add the task without a total first.
                # The description will dynamically change with the status update.
                task_id = progress.add_task("[yellow]Starting...", start=False)
                # The pull function streams the download progress
                for update in ollama.pull(model_tag, stream=True):
                    status = update.get("status", "...")
                    completed = update.get('completed', 0)
                    total = update.get('total', None)
                    
                    if total is not None and not progress.tasks[task_id].started:
                        # Set the total once we know it and start the task timer
                        progress.update(task_id, total=total, description=f"[blue]Downloading {model_tag}")
                        progress.start_task(task_id)
                    
                    # Update the progress bar with the current values
                    progress.update(
                        task_id,
                        completed=completed,
                        description=f"[blue]{status} {model_tag}" if status != "downloading" else None
                    )

                # Once the loop finishes, the download is complete.
                # Mark the task as finished and update the description one last time.
                progress.update(task_id, description=f"[green]Download complete: {model_tag}", completed=total, refresh=True)

            screen.console.print(f"Download of {model_tag} complete.")
            self.model=model_tag
                

    def get_models_list(self)-> List[str]:
        """Fetches a list of locally available models from Ollama."""
        try:
            models_data = ollama.list()
            models = [model['model'] for model in models_data.get('models', [])]
            return models
        except Exception as e:
            console.print(f"[bold red]Error connecting to Ollama service:[/bold red] {e}")
            console.print("Please ensure Ollama is installed and running.")
            sys.exit(1)

    def select_model(self,model_num: Optional[int] = None) -> None:
        """
        function to select a model from the list.
        Parameters
        ----------
        model_num: int
            \nmodel number to select the model from the model list.\n
        """
        models_list=self.get_models_list()
        if model_num:
            self.model=models_list[model_num - 1]
        else:
            with console.screen(style="bold white on red") as screen:
                if not models_list:
                    screen.console.print("[bold yellow]No models found.[/bold yellow] Please pull a model (e.g., 'ollama pull llama3') first.")
                    sys.exit(1)
                table = Table(title=Panel("[bold cyan]Available models:[/bold cyan]", title="Model Selection"))
                heading=Padding("Model",(0,4,0,4))
                table.add_column("SNo", justify="center", style="cyan", no_wrap=True)
                table.add_column(heading,justify="center", style="magenta")
                for i, model in enumerate(models_list):
                    table.add_row(f"{i + 1}", f"{model}")
                screen.console.print(table)
                while True:
                    try:
                        choice = console.input(f"Enter the number of the model you want to use ([1-{len(models_list)}]): ")
                        choice = int(choice)
                        if 1 <= choice <= len(models_list):
                            self.model=models_list[choice - 1]
                            break
                        else:
                            screen.console.print("[bold red]Invalid choice.[/bold red] Please enter a number within the valid range.")
                    except ValueError:
                        console.print("[bold red]Invalid input.[/bold red] Please enter a number.")

    # --------------------------------------------------------------------- #
    # Chat interface
    # --------------------------------------------------------------------- #
    def chat(self, user_question: Optional[str] = None) -> str:
        """
        Stream the response from the selected model, render it with Rich,
        and finally **return** the full response string.

        Parameters
        ----------
        user_question: str
            The prompt you want the LLM to answer.

        Returns
        -------
        str
            The complete answer generated by the model.
        """
        if not self.model:
            # If the caller hasn't set a model yet, ask them to pick one.
            self.select_model()
        console.rule("\n[bold green]Model Response.[/bold green]")
        messages = [{"role": "user", "content": user_question}]
        full_response = ""
        with Live(console=console, screen=False,refresh_per_second=10,vertical_overflow='visible') as live:
            try:
                response_stream = ollama.chat(model=self.model, messages=messages, stream=True)
                for chunk in response_stream:
                    content = chunk["message"]["content"]
                    full_response += content
                    live.update(Markdown(full_response))
            except ollama.ResponseError as exc:
                self._handle_ollama_error(exc)
            except Exception as exc:  # pragma: no cover
                self._handle_ollama_error(exc)

        console.rule("\n[bold green]Response complete.[/bold green]")
        return full_response

    # ------------------------------------------------------------------ #
    # 2️⃣ Yield‑as‑you‑go mode (the new requirement)
    # ------------------------------------------------------------------ #
    def chat_yield(self, user_question: str) -> Generator[str, None, None]:
        """
        Stream the answer **and yield each chunk** as it arrives.

        The caller can iterate over the generator to receive partial results
        in real-time, e.g.:

        ```python
        for part in llm.chat_yield("Tell me a joke"):
            print(part, end="", flush=True)
        ```

        The method also updates a live Rich view so you still get the nice
        on-screen rendering when you run the script directly.
        """
        if not self.model:
            # If the caller hasn't set a model yet, ask them to pick one.
            self.select_model()
        messages = [{"role": "user", "content": user_question}]
        full_response = ""

        try:
            stream = ollama.chat(model=self.model, messages=messages, stream=True)
            for chunk in stream:
                txt = chunk["message"]["content"]
                full_response += txt
                # Yield the newest piece to the caller
                yield txt
        except ollama.ResponseError as exc:
            self._handle_ollama_error(exc)
        except Exception as exc:  # pragma: no cover
            self._handle_ollama_error(exc)

# --------------------------------------------------------------------------- #
# Example usage when run as a script (optional)
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    llm = LLM()
    # Uncomment the next line if you need to pull a fresh model first:
    # llm.download_model()
    prompt="explain AI in 100 words"
    # ----- Mode 1: get the whole answer at once -----
    full = llm.chat(prompt)
    print("\n--- Full answer captured as a string ---\n", full)

    # ----- Mode 2: stream and yield -----
    print("\n--- Streaming with yield (printing as we go) ---")
    for piece in llm.chat_yield(prompt):
        # `piece` is the newest fragment from Ollama.
        print(piece, end="", flush=True)