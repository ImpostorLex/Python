import sqlite3
from datetime import date
import typer

app = typer.Typer()
today = date.today()

# Iniates connection to the database
conn = sqlite3.connect("/home/root-a/Documents/Python/Anything/habit-tracker/totrack.db")
conn.execute("PRAGMA foreign_keys = 1")
# Enable us to execute and fetch SQL queries.
c = conn.cursor()

def create_table():
    c.execute("""CREATE TABLE if not exists habits(
    habit text,
    category text,
    date_added text,
    total_hours integer)
    """)

    c.execute("""CREATE TABLE if not exists history(
    habit text,
    category text,
    date_added text,
    hours integer,
    minutes integer)
    """)

def insert_habit(habit, category):
    habit_is_exists = c.execute('Select habit from habits').fetchall()

    stripped_habit = []
    for x in range(0, len(habit_is_exists)):
        stripped_habit.append(habit_is_exists[0][0].replace("''", " "))


    if habit in stripped_habit:
        typer.echo("It looks like that habit already exists")
    
    else:  
        typer.echo(f"Adding {habit} to the list.")
        c.execute('Insert into habits values(:habit, :category, :date_added, :total_hours)', {'habit': habit, 'category': category, 'date_added': today, 'total_hours': 0})
        c.execute('Insert into history values(:habit, :category, :date_added, :hours, :minutes)', {'habit': habit, 'category': category, 'date_added': today, 'hours': 0, 'minutes': 0})
        conn.commit()


def show_all():
    all = c.execute('SELECT * FROM habits').fetchall()
    habits = []

    for habit in all:
        habits.append(habit)
    
    return habits

def show_history(param):
    all = c.execute('SELECT * FROM history where habit = :habit', {'habit':param}).fetchall()
    habits = []

    for habit in all:
        habits.append(habit)
    
    return habits

stripped_all = []
hours = []
mins = []
to_hrs = 0

def insert_time(hour, minutes, habit):
    global to_hrs
    all = c.execute('SELECT habit, total_hours, category FROM habits where habit = :habit', {'habit':habit}).fetchall()  
    
    if all != []:
        
        # Replacing the the single quote mark
        for x in range(0, 3):
            try:
                strip_content = all[0][x].replace("''", " ")
            except:
                strip_content = all[0][x]
            stripped_all.append(strip_content)

        habit_history = c.execute("Select hours, minutes from history where habit = :habit", {'habit':habit}).fetchall()
        for x in range(0, len(habit_history)):
            hours.append(habit_history[x][0])
            mins.append(habit_history[x][1])

        # Calculation of hours and minutes.
        print(mins)
        hrs_sum = sum(hours)
        mins_sum = sum(mins)

        if mins_sum >= 60:
            to_hrs = round((mins_sum / 60), 2)
            print(to_hrs)
        
        total_time = to_hrs + hrs_sum
        c.execute("Update habits set total_hours  = :total_hours where habit = :habit", {'total_hours': total_time, 'habit': habit})
        c.execute("Insert into history values(:habit, :category, :date_added, :hours, :minutes)", {'habit': habit, 'category': stripped_all[2], 'date_added': today, 'hours': hour, 'minutes': minutes})
        conn.commit()
        typer.echo("Thank yourself for putting in time. Cheers")

    else:
        typer.echo("Oops it looks like that habbit does not exists")


create_table()