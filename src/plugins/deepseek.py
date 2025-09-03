import ollama
import typer
from rich.console import Console
from pyright import List, Tuple, Optional

app: Any = typer.Typer(help="AI command. Allows you to communicate with your local LLMs")


def _connect_with_ollama(prompt: str):
    try:
        response = ollama.chat(
            model="deepseek-r1:8b",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            stream=False,
        )
        # typer.echo(f"Received response from Ollama: {response['message']['content'].strip()}")
        return response['message']['content'].strip()
    except ollama.ResponseError as e:
        typer.echo(f"Error communicating with Ollama: {e}", err=True)
        typer.echo(f"Failed to communicate with Ollama: {e}", err=True)

        typer.echo("If you don't have ollama installed, you can install it by going through the instructions on "
                   "their website: https://ollama.com/ and installing a deepseek model")
        raise


@app.command()
def chat(prompt: str):
    """
    Chat with the AI model based on the provided prompt.

    Args:
        prompt (str): The prompt to start the conversation.
    """
    # typer.echo(f"Starting chat with prompt: {prompt}")

    try:
        # Interact with the Ollama LLM
        response = _connect_with_ollama(prompt)
        typer.echo(f"🤖 Deepseek response:\n{response}")

    except Exception as e:
        typer.echo(f"Error chatting with AI: {e}", err=True)
        typer.echo(f"Failed to chat with AI: {e}", err=True)