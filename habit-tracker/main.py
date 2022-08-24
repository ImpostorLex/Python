from ast import Str
from rich.console import Console
from rich import print
from rich.table import Table
import typer
from database import insert_habit, show_all, insert_time, show_history


# Creating the objects from the library.
console = Console()
app = typer.Typer()

def view_habit():
    table = Table(title="My Habits")
    table.add_column("Habit", justify="right", style="cyan", no_wrap=True)
    table.add_column("Category", justify="right", style="green")
    table.add_column("Date Added", justify="right", style="blue")
    table.add_column("Total Hours", justify="right", style="red")
    show = show_all()

    for x in range(0, len(show)):
        table.add_row(show[x][0], show[x][1], show[x][2], str(show[x][3]))

    console.print(table)

def view_history(track):
    table = Table(title="My Habits")
    table.add_column("Habit", justify="right", style="cyan", no_wrap=True)
    table.add_column("Category", justify="right", style="green")
    table.add_column("Date Added", justify="right", style="blue")
    table.add_column("Hours", justify="right", style="red")
    table.add_column("Minutes", justify="right", style="yellow")

    show = show_history(track)

    for x in range(0, len(show)):
        table.add_row(show[x][0], show[x][1], show[x][2], str(show[x][3]), str(show[x][4]))

    console.print(table)

@app.command(short_help="Shows table")
def habit():
    view_habit()


@app.command(short_help="Adds a habit to the tracker. REQUIRED [HABIT] [CATEGORY]")
def add(habit : str, category : str):
    insert_habit(habit, category)
    view_habit()


@app.command(short_help="Add hours and minutes, leave 0 if it only took exactly one hour or minutes only. REQUIRED [HABIT] [HOUR], [MINUTE]")
def time(habit: str, hour: int, min: int):
    if min > 60:
        typer.echo("If it took 60 minutes just add one hour instead.")
    else:
        typer.echo("Inserting record.")
        insert_time(hour, min, habit)
    view_habit()

@app.command(short_help="Show a specfic habit history")
def history(habit : str):
    view_history(habit)


if __name__ == "__main__":
    app()