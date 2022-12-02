from ast import Str
from rich.console import Console
from rich import print
from rich.table import Table
import typer
from database import insert_habit, show_all, insert_time, show_history, remove, update_habit, month


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
    if show:
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


@app.command(short_help="Delete a habit history will be also deleted. REQUIRED [HABIT]")
def delete(habit: str):
    decision = typer.prompt(f"Are you sure you want to delete {habit}, [Y/n]? ")

    if decision == 'Y':
        remove(habit)
        view_habit()
        typer.echo(f"Deletion of habit {habit} succesful.")
    elif decision == 'N':
        typer.echo(f"Deletion of habit {habit} cancelled.")
    else:
        typer.echo("Incorrect input type 'Y' or 'n' only.")


@app.command(short_help="Update a category or a habit. REQUIRED ['H' for habit and 'C' for category]], [OLD VALUE] [NEW VALUE]")
def update(field: str, old_val: str, new_val : str):
    if field == 'H' or field == "C":            
        is_succesful = update_habit(field, old_val, new_val)

        if is_succesful:
            view_history(new_val)
        else:
            typer.echo("It looks like that does not exist")
        
    else:
        typer.echo("Wrong input.")

@app.command(short_help="Show the a graph total hours per month REQUIRED [habit] [year]")
def graph(habit: str, year:int):
    not_exists = month(habit, year)

    if not_exists == "1":
        typer.echo(f"It looks like you are in your first month of that habit {habit} or perhaps wrong year?")

    

if __name__ == "__main__":
    app()