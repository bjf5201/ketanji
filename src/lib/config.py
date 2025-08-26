import sqlite3

import typer
from rich import print
from rich.table import Table

from ketanji.lib.utils import config_sqlite_file, _refresh_plugins, get_db_connection

app = typer.Typer(help="Config management")

@app.command(name="init")
def initialize_config() -> None:
  """Initialize an sqlite db that stores the config"""
  if config_sqlite_file.exists():
    delete_old = typer.confirm("This file already exists. Do you want to delete it?")

    if not delete_old:
      return

    # remove the old file
    config_sqlite_file.unlink()

  conn = get_db_connection()
  cursor = conn.cursor()

  # Create tables for db
  cursor.execute("""
  CREATE TABLE IF NOT EXISTS configs (
      name TEXT PRIMARY KEY,
      enabled BOOLEAN NOT NULL
  )
  """)

  cursor.execute("""
  CREATE TABLE IF NOT EXISTS plugins (
      name TEXT PRIMARY KEY,
      enabled BOOLEAN NOT NULL
  )
  """)

  conn.commit()
  conn.close()

  # load available plugins
  _refresh_plugins()

@app.command(name="set")
def set_config_value(key: str, value: str) -> Table | None:
  """Set a value for a config key"""
  conn = None
  try:
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute("""
          INSERT INTO configs (key, value)
          VALUES (?, ?)
          ON CONFLICT(key) DO UPDATE SET value=excluded.value
          """, (key, value))
      conn.commit()
      print(f"[green]Configs set:[/] {key} = {value}")
  except sqlite3.OperationalError as e:
      if "no such table" in str(e):
          print("[red]ketanji configs not initialized. Use [white]`ketanji init`[red] to initialize.")
      else:
          print(f"Error: {e}")
  finally:
        if conn:
          conn.close()


@app.command(name="get")
def get_config_value(key: str) -> None:
    """Get value of a key set in ketanji configs"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM configs WHERE name = ?", (key,))
        row = cursor.fetchone()

        if row:
            value = row[0]
            print(f"[blue]{key}[/]: {value}")
        else:
            print(f"[red]Config key [white]'{key}'[red] not found.[/]")
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print("[red]ketanji configs not initialized. Use [white]`ketanji init`[red] to initialize[/]")
        else:
            print(f"Error: {e}")
    finally:
        if conn:
            conn.close()


@app.command(name="list")
def list_configurations() -> None:
    """List all key-value pairs in the configs"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM configs")
        rows = cursor.fetchall()

        if not rows:
            print("[yellow] No configs found.[/]")
            return

        table = Table(title="Configs")
        table.add_column("Key", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        for key, value in rows:
            table.add_row(key, value)

        print(table)

    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print("[red]ketanji configs not initialized. Use [white]`ketanji init`[red] to initialize[/]")
        else:
            print(f"Error: {e}")
    finally:
        if conn:
            conn.close()