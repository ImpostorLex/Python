from nis import cat
from re import M
import sqlite3
from datetime import date, datetime
from webbrowser import get
import typer
from icecream import ic
import matplotlib.pyplot as plt
import seaborn as sns
import calendar

app = typer.Typer()
today = date.today()

# Iniates connection to the database
conn = sqlite3.connect("/home/root-a/Documents/Python/Anything/habit-tracker/Version 2/totrack.db")
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
        stripped_habit.append(habit_is_exists[0][0].replace("''", " ").lower())


    if habit.lower() in stripped_habit:
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

def show_history(find):
    all = c.execute('SELECT * FROM history where habit = :habit', {'habit':find}).fetchall()
    habits = []

    if all:
        for habit in all:
            habits.append(habit)
        
        return habits
    else:
        typer.echo(f"It looks like that habit {habit} does not exist")

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
            ic(x)
            hours.append(habit_history[x][0])
            mins.append(habit_history[x][1])

        
        # Calculation of hours and minutes.
        hrs_sum = sum(hours)
        mins_sum = sum(mins) + minutes
        ic(hrs_sum, mins_sum)

        if mins_sum >= 60:
            to_hrs = round((mins_sum / 60), 2)
            
        
        total_time = to_hrs + hrs_sum + hour
        c.execute("Update habits set total_hours  = :total_hours where habit = :habit", {'total_hours': total_time, 'habit': habit})
        c.execute("Insert into history values(:habit, :category, :date_added, :hours, :minutes)", {'habit': habit, 'category': stripped_all[2], 'date_added': today, 'hours': hour, 'minutes': minutes})
        conn.commit()
        typer.echo("Thank yourself for putting in time. Cheers")


    else:
        typer.echo("Oops it looks like that habbit does not exists")


def remove(habit):
    habit_exists = c.execute("Select habit from habits where habit = :habit", {'habit': habit}).fetchone()

    if habit_exists:
        c.execute("Delete from habits where habit = :habit", {'habit': habit})
        c.execute("Delete from history where habit = :habit", {'habit': habit})
        conn.commit()
    else:
        typer.echo("It looks like that habit does not exists")

def update_habit(field, old, new):
    habit_exist = c.execute("Select * from habits where habit = :habit", {'habit': old}).fetchone()
    

    if habit_exist:

        if field == 'H' and habit_exist[0] == old:
            c.execute('update habits set habit = :habit where habit = :old_habit', {'habit': new, 'old_habit':old})
            c.execute('update history set habit = :habit where habit = :old_habit', {'habit': new, 'old_habit':old})
            conn.commit()
            return True

        elif field == "C" and habit_exist[1] == old:
            c.execute('update habits set category = :habit where habit = :old_habit', {'habit': new, 'old_habit':old})
            c.execute('update history set category = :habit where habit = :old_habit', {'habit': new, 'old_habit':old})
            conn.commit()
            return True
        else:
            return False

def month(habit:str, year:int):
    yr = []
    mths = []
    day = []
    hrs = []
    mins = []

    unq_mths = []
    before_month = 0
    ctr = 0
    ctr2 = 0
    total_hrs_per_month = []
    to_hrs = 0
    months_in_names = []

    habit_exist = c.execute("Select * from habits where habit = :habit", {'habit': habit}).fetchone()

    if habit_exist:
        # Returns a list of tuples with a format of Year - Month - Day
        get_date = c.execute("Select date_added, hours, minutes from history where habit = :habit", {'habit':habit}).fetchall()   
               
        to_date = [datetime.strptime(get_date[x][0], "%Y-%m-%d").date() for x in range(0, len(get_date))]
        
        # Seperating month, day andd summing up hours and mins.

        for x in range(0, len(get_date)):

            if to_date[x].month not in unq_mths:
                
                unq_mths.append(to_date[x].month)

                yr.append(to_date[x].year)
                mths.append(to_date[x].month)
                day.append(to_date[x].day)

        if len(unq_mths) <= 1 or year not in yr:
                return "1"

        while ctr != len(unq_mths):         
            
            before_month = to_date[ctr].month

            for x in range(ctr2, len(get_date)):

                if int(to_date[x].month) == before_month:
                    mins.append(get_date[x][2])
                    hrs.append(get_date[x][1])
                    
                    if sum(mins) > 60:
                        to_hrs = round((sum(mins) / 60), 2)
                             

                # If iterated new month is not the same as the before math change the value of before_month to new recent iterated month
                elif int(to_date[x].month) != before_month:
                    total_hrs_per_month.append(to_hrs + sum(hrs))

                    before_month = int(to_date[x].month)           
                    ctr2 = x
                    ctr += 1
                    mins.clear()
                    hrs.clear()
                    to_hrs = 0

        # Output is correct :- [8.6, 42.93, 19.22] - total_hrs
        months_in_names = [calendar.month_name[num] for num in unq_mths]

        plt.figure(figsize=(10,7), dpi=120)
        plt.title(f'Total hours spend on {habit} per month', fontsize=18)
        plt.yticks(fontsize=14)
        plt.xticks(fontsize=14, rotation=45)

        ax1 = plt.gca()

        sns.barplot(x=months_in_names, y=total_hrs_per_month, palette="rocket", ax=ax1)
        ax1.axhline(0, color="k", clip_on=False)
        ax1.set_ylabel("Hours")
        ax1.xaxis.label.set_color('Purple')   

        plt.show()
   
        # Returns 57 sets. - Hack

create_table()