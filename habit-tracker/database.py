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

    if habit in habit_is_exists:
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
    all = c.execute(f'SELECT * FROM history where habit = :habit', {'habit':param}).fetchall()
    habits = []

    for habit in all:
        habits.append(habit)
    
    return habits


def insert_time(hour, minutes, habit):

    all = c.execute('SELECT habit FROM habits').fetchall()   
    stripped_all = []

    for x in range(0, len(all)):
        strip_str = all[x][0].replace("''", " ")
        typer.echo(strip_str)
        stripped_all.append(strip_str)

    if habit.lower() in stripped_all: 
        total_time = hour + minutes
        c.execute("Update habits set total_hours  =  ? where habit = ?", (total_time, habit))
        c.execute("Update history set hours = ?, date_added = ? , minutes = ? where habit = ?", (hour, today,minutes, habit))
        conn.commit()
        typer.echo("Thank yourself for putting in time. Cheers")
    else:
        typer.echo("Oops it looks like that habbit does not exists")


create_table()