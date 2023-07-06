import sqlite3
from datetime import datetime
import typer
from icecream import ic
app = typer.Typer()
now = datetime.now()
todays_date = now.strftime('%Y-%m-%d')


# Iniates connection to the database
conn = sqlite3.connect(
    "./workout-tracker.db")
# Enable PRAGMA to enforce foreign key constraints
conn.execute("PRAGMA foreign_keys = 1")

# Enable us to execute and fetch SQL queries.
c = conn.cursor()


def create_table():
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS program(
    id integer primary key,
    workout text,
    reps integer,
    sets integer,
    category text
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS log(
    id integer primary key,
    program_id integer,
    reps integer,
    sets integer,
    mood_id integer,
    date_added text,
    FOREIGN KEY (program_id) REFERENCES program(id),
    FOREIGN KEY (mood_id) REFERENCES mood(id),
    FOREIGN KEY (date_added) REFERENCES total_hours(id)
    )
    """)

    c.execute("""CREATE TABLE IF NOT EXISTS mood(
    id integer primary key,
    name text
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS total_hours(
    id text primary key,
    hours integer,
    minutes integer
    )""")

# Fix this


def add_log_entry(name, reps, sets, mood, duration_hours, duration_minutes):
    try:

        get_program_id = c.execute("SELECT id FROM program where workout = :workout", {
                                   "workout": name}).fetchone()

        # Tuple unpacking, if expecting one data only we can use this method.
        value, = get_program_id

        if value:

            # Insert the total duration of workout session, only ask once per day, if already filled.
            if duration_hours == 0 or duration_minutes == 0:
                c.execute("INSERT INTO total_hours (id, hours, minutes) VALUES (?, ?, ?)",
                          (todays_date, duration_hours, duration_minutes))
                conn.commit()

            get_date = c.execute("SELECT id from total_hours where id = :date_added", {
                "date_added": todays_date}).fetchone()

            # Get the mood_id first.
            mood_id = c.execute("SELECT id FROM mood where id = :id",
                                {"id": mood}).fetchone()
            ic(value, mood_id[0])
            c.execute("INSERT INTO log(program_id, reps, sets, mood_id, date_added) VALUES (:id, :reps, :sets, :mood, :date_added)",
                      {"id": value, "reps": reps, "sets": sets, "mood": mood_id[0], "date_added": get_date[0]})
            conn.commit()

            return "Logged successfully, thank yourself for doing this!"

        else:
            return "Program name not found."

    except sqlite3.Error as e:
        return "An error occurred:", str(e)


def add_workout(name, category, reps, sets):

    try:
        c.execute("INSERT INTO program(workout, reps, sets, category) VALUES(:name, :reps, :sets, :category)", {
            "name": name, "reps": reps, "sets": sets, "category": category})
        conn.commit()

    except sqlite3.Error as e:
        return "An error occurred:", str(e)


def workouts(name):

    workouts = c.execute("Select workout from program where workout = :workout_to_be_added", {
        "workout_to_be_added": name}).fetchall()

    return workouts


entire_program = []


total_hours = 0


def print_workout_program():

    rows = c.execute(
        "SELECT program.id, program.workout, program.reps, program.sets, program.category from program").fetchall()

    if rows:
        for row in rows:
            total_hours_rows = c.execute(
                "SELECT SUM(hours), SUM(minutes) FROM total_hours").fetchall()

            # Count the number of instances for each program, where each instance represents
            # a workout session of a specific workout

            activity_per_workout = c.execute(
                "SELECT COUNT(*) from log WHERE program_id = :program_id", {"program_id": row[0]})
            entire_program.append(
                (row[1], row[2], row[3], row[4], activity_per_workout.fetchone()[0] or 0))

        return entire_program, total_hours_rows
    else:
        return None


def check_log_date(today_date):

    is_already_logged = c.execute(
        "SELECT date_added from log where date_added = :date_added", {"date_added": today_date}).fetchone()

    return is_already_logged


def compare_data_to_file(program_names, changes):

    for program in program_names:

        # No need to check if program exists, it is checked at line 107 in main.py
        reps, sets = c.execute("SELECT reps, sets FROM program where workout = :program", {
                               "program": program[0]}).fetchone()

        # If there is any changes compared to database and changes is equals to True
        # Then allow the changes
        new_reps = program[1]
        new_sets = program[2]

        if (reps != new_reps or sets != new_sets) and changes == False:
            return "Not allowed"

        elif (reps != new_reps or sets != new_sets) and changes == True:
            c.execute("UPDATE program SET reps = :reps, sets = :sets WHERE workout = :program", {
                      "reps": new_reps, "sets": new_sets, "program": program[0]})
            conn.commit()
            return "Allowed"
        else:
            raise Exception


def workout_summary(name, year):

    # Check if workout exists
    workout_exists = c.execute("SELECT id FROM program where workout = :workout", {
                               "workout": name}).fetchone()

    if workout_exists:

        # The || -%-% is used to concatante the YEAR with the wildcard, % = any
        result = c.execute(
            "SELECT reps, sets, mood_id, date_added where program_id = :p_id AND LIKE :year",
            {"p_id": workout_exists[0], "year": f"{year}-%-%"}).fetchall()

        typer.echo(result)


create_table()
