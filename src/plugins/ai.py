import subprocess
import typer
import json

def check_ollama_installed() -> bool:
    try:
        subprocess.run(['ollama', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_deepseek_pulled() -> bool:
    try:
        proc = subprocess.run(['ollama', 'list', '--json'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        models = json.loads(proc.stdout)
        # Ollama's `list --json` returns a JSON array of models.
        for model in models:
            if model.get('name', '') == 'deepseek-r1':
                return True
        return False
    except Exception:
        return False

def pull_deepseek():
    typer.echo("Pulling deepseek-r1 model...")
    try:
        subprocess.run(['ollama', 'pull', 'deepseek-r1'], check=True)
        typer.echo("Successfully pulled deepseek-r1 model for Ollama!")
    except subprocess.CalledProcessError as e:
        typer.echo(f"Failed to pull deepseek-r1 model: {e}", err=True)
        typer.echo("You can manually run: ollama pull deepseek-r1", err=True)

def check_and_install_deepseek_r1():
    """
    Checks if Ollama is installed and if deepseek-r1 model is present.
    Pulls the model if not already installed.
    """
    typer.echo("Checking Ollama installation...")
    if not check_ollama_installed():
        typer.echo(
            "Ollama is not installed or not available in your PATH.\n"
            "Please install Ollama first by following instructions at https://ollama.com/download\n",
            err=True
        )
        return

    typer.echo("Ollama is installed.")
    if is_deepseek_pulled():
        typer.echo("deepseek-r1 model is already installed!")
    else:
        pull_deepseek()

@app.command()
def init():
    """
    Initializes the plugin and ensures deepseek-r1 is available for Ollama.
    """
    check_and_install_deepseek_r1()