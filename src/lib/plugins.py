import sqlite3

import typer
from pyright import Array, Any
from rich import print
from rich.table import Table

from ketanji.lib.utils import _refresh_plugins, get_plugin_list, get_db_connection

PROTECTED_PLUGINS: Array = ["config", "plugin"]

app:Any = typer.Typer(help="Commands to manage plugins")

@app.command(name="list")
def list_plugins() -> None:
    """List all available plugins"""
    rows = get_plugin_list()

    if not rows:
        print("[yellow] No plugins found.[/]")
        return

    table = Table(title="Ketanji Plugins")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Enabled")

    for key, value in rows:
        table.add_row(key, "[cyan]Yes[/]" if value == 1 else "[magenta]No[/]")

    print(table)


@app.command(name="plug")
def plug_plugins(name: str) -> None:
    """Enable (or 'plug in') a plugin"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, enabled FROM plugins WHERE name = ?", (name,))
        rows = cursor.fetchone()

        if not rows:
            print(f"[red] Plugin {name} not found.[/]")
            return

        cursor.execute("UPDATE plugins SET enabled=TRUE WHERE name = ?", (name,))
        conn.commit()
        print(f"[green] Enabled aka 'plugged in' the plugin {name}.[/]")

    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print("[red]ketanji config not initialized. Use [white]`ketanji init`[red] to initialize[/]")
        else:
            print(f"Error: {e}")
    finally:
        if conn:
            conn.close()


@app.command(name="unplug")
def unplug_plugins(name: str) -> None:
    """Disable (or 'unplug') a plugin"""
    if name in PROTECTED_PLUGINS:
        print(f"[italic]{name}[/] [red]is an internal plugin that cannot be disabled[/]")
        return

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, enabled FROM plugins WHERE name = ?", (name,))
        rows = cursor.fetchone()

        if not rows:
            print(f"[red] Plugin {name} not found.[/]")
            return

        cursor.execute("UPDATE plugins SET enabled=FALSE WHERE name = ?", (name,))
        conn.commit()
        print(f"[green]Disabled aka 'unplugged' plugin {name}.[/]")

    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print("[red]ketanji config not initialized. Use [white]`ketanji init`[red] to initialize[/]")
        else:
            print(f"Error: {e}")
    finally:
        if conn:
            conn.close()


@app.command(name="refresh")
def refresh_plugins() -> None:
    """Re-discovers all available plugins and enables them"""
    _refresh_plugins()