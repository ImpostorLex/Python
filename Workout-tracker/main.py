import typer
from rich import print
from rich.table import Table
from rich.console import Console
from database import add_log_entry, workouts, add_workout, print_workout_program, check_log_date, compare_data_to_file, workout_summary
from icecream import ic
from typing import Optional
from datetime import datetime, timedelta
from print_messages import print_mood, print_muscle_groups, muscle_groups, moodNumError, isWorkoutExist, lineLength
console = Console()
app = typer.Typer()


total_hours = 0
now = datetime.now()
todays_date = now.strftime('%Y-%m-%d')

# ------------------- USER DEF FUNCTIONS -------------------

program_names = []


def check_changes_in_file(data, changes):

    if data:
        for sublist in data:
            # *_ is used as a placeholder to tell the rest of the value from sublist
            # is ignored and not needed.
            name, reps, sets = sublist
            program_names.append((name, reps, sets))

        has_error = compare_data_to_file(program_names, changes)


x_list = []


def process_file(file_path):
    ctr = 0
    # Opening a file using open in python creates an object which supports line by line iteration
    # [['Hammer Curls', ' 2', '2', '2'], ['Bicep Curls', ' 2', '2', '2']] output
    try:
        with open(file_path, "r") as file:
            # Format: name, reps, sets, mood_number
            for line in file:
                try:

                    ctr += 1
                    x = line.strip().split(',')
                    # Check if line has more argument than required or less than required.
                    if len(x) != 4:
                        raise lineLength(
                            f"There is a line in line {ctr}that has more/less than the required")
                    x_list.append(x)
                except lineLength as e:
                    typer.echo(
                        f"{e}. The format should be\nworkout-name, #reps, #sets, #mood seperated by a comma")
                else:
                    return x_list
    except FileNotFoundError:
        typer.echo("File not found, please try again.")


def log_workout_from_file(file_path: str, duration_hours, duration_minutes, changes):

    has_error = False

    try:
        file = process_file(file_path)
        # Validate the data
        for x in range(len(file)):
            try:
                is_workout_exists = workouts(file[x][0])
                int(file[x][1])
                int(file[x][2])
                mood_num = int(file[x][3])

                if not (1 <= mood_num <= 5):
                    raise moodNumError("Mood numbers are only 1 to 5")

                if not is_workout_exists:
                    raise isWorkoutExist("Workout does not exists")

            except ValueError:
                typer.echo(
                    "Input error, the format for file is workout-name, #reps, #sets, #mood seperated by a comma")
                has_error = True
                break
            except moodNumError as m:
                typer.echo(f"{m}\n{print_mood}")
                has_error = True
                break
            except isWorkoutExist as w:
                typer.echo(f"{file[x][0]} {w}")
                has_error = True
                break

        # If there is no error then it is safe to assume all data is validated and correct
        # We can safely use the x_list following the format: name, reps, sets, mood_num
        if has_error == False:

            for x in range(len(file)):

                msg = add_log_entry(file[x][0], file[x][1],
                                    file[x][2], file[x][3], duration_hours, duration_minutes)

                # Compared reps and sets to database check for changes.
                is_changes_allowed = check_changes_in_file(file, changes)
            if is_changes_allowed == "Allowed":
                typer.echo(typer.style(
                    f"{msg}", fg=typer.colors.GREEN))
            elif is_changes_allowed == "Not allowed":
                typer.echo(
                    "Please specify the --update/-u flag to allow changes to the reps and sets data.")
    except Exception as e:
        typer.echo(f"An error has occured: {str(e)}")


def log_workout_line_by_line(duration_hours, duration_minutes, changes):
    name = typer.prompt("Enter workout name")
    reps = typer.prompt("Enter number of reps", type=int)
    sets = typer.prompt("Enter number of sets", type=int)
    mood = typer.prompt(f"{print_mood}\nEnter mood num:", type=int)

    # Make sure if changes in the sets and reps input is allowed.
    program_names = [name, reps, sets]
    changes_allowed = compare_data_to_file(program_names, changes)

    if not (mood < 1 and mood > 5) and changes_allowed == "Allowed":
        x = add_log_entry(name, reps, sets,
                          duration_hours, duration_minutes)

        typer.echo(x)
    else:
        typer.echo("An error has occurred.")


# ------------------- ^ USER DEF FUNCTIONS  ^ -------------------


@app.command(short_help="Shows the summary for all your workouts.")
def summary():
    table = Table(title="Summary")
    table.add_column("Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Reps", justify="right", style="cyan", no_wrap=True)
    table.add_column("Sets", justify="right", style="cyan", no_wrap=True)
    table.add_column("Category", justify="right", style="cyan", no_wrap=True)
    table.add_column("Activity", justify="right", style="cyan", no_wrap=True)

    results = print_workout_program()

    if results is not None:
        entire_program, total_hours_rows = results
        for item in entire_program:
            name, reps, sets, category, activity = item
            table.add_row(name, str(reps), str(sets), category, str(activity))

        sum_hours = total_hours_rows[0][0] if total_hours_rows and total_hours_rows[0][0] is not None else 0
        sum_minutes = total_hours_rows[0][1] if total_hours_rows and total_hours_rows[0][1] is not None else 0

        days = sum_hours / 24 or 0
        hours = sum_hours + (sum_minutes / 60) or 0

        console.print(table)
        typer.echo(
            f"You have been working out for {round(hours,2)} hour(s) or {round(days,2)} day(s)")
    else:
        typer.echo("No program found.")


@app.command(short_help="Show history of a specific workout. Required: [HABIT] and [YEAR], Optional: [--asc] or [-a] for ascending order and [--graph] or [-g] to show data in a bar graph (These optional options don't need data just include the flags) leave empty if not desired ")
def workout(name: str, year: int, graph: bool = typer.Option(False, "--graph", "-g", help="Show the data into a bar graph")):

    show_summary = workout_summary(name, year)


@app.command(short_help="Create a workout to track, REQUIRED [WORKOUT] - [CATEGORY] - [REPS] - [SETS], OPTIONAL [--numbers/-n] allow the use of numbers in workout_name, [-c] prints out the muscle categories")
def create(name: str, category: str, reps: int, sets: int,
           cn: bool = typer.Option(
               False, "--numbers", '-n', help="Allow the use of numbers as part of the workout name or category")):

    # Validate data
    is_workout_exists = workouts(name)

    if is_workout_exists:
        typer.echo("It looks like that workout exists already.")
    else:
        if cn or name.isalpha() or category.isalpha():
            add_workout(name, category, reps, sets)
            typer.echo("Workout addition successfully.")
        elif name.isalpha() or name.isdigit():
            typer.echo(
                "Numbers are allowed by adding the flag --numbers or -n but no non-alphabet characters are allowed.")


duration_hours = 0
duration_minutes = 0


@app.command(short_help="Log a existing workout one by one or per muscle group or specific muscle groups at once.")
def log(
    file: str = typer.Option(
        None, "--file", "-f", help="Log a workout using a file"),
    line: bool = typer.Option(False, "--manual", "-m",
                              help="Log a workout using line by line prompting."),
    changes: bool = typer.Option(
        False, "--update", "-u", help="Expect and allow changes from sets and reps, usually means user got stronger or change in program")
):

    already_logged = check_log_date(todays_date)

    if not already_logged:
        typer.echo(
            "Input duration of workout session in hours and minutes")
        # Make duration_hours and minutes global because they are assigned inside a block
        # making them a local var.
        global duration_hours
        duration_hours = typer.prompt("Enter hours", type=float)
        global duration_minutes
        duration_minutes = typer.prompt("Enter minutes", type=float)

    if file:
        log_workout_from_file(file, duration_hours, duration_minutes, changes)
    elif line:
        log_workout_line_by_line(duration_hours, duration_minutes, changes)
    else:
        typer.echo("Please provide either --file/-f or --manual/-m option.")


if __name__ == "__main__":
    app()
