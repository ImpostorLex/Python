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

    hrs = 0
    mins = 0
    ctr = 0
    hr_and_mins_per_month = []
    existing_months = []

    habit_exist = c.execute("Select * from history where habit = :habit and date_added LIKE :year", {'habit': habit, "year": f"%{year}%"}).fetchone()

   
    if habit_exist:
        
        get_date = c.execute("Select date_added, hours, minutes from history where habit = :habit and date_added LIKE :year", {'habit':habit, 'year': f"%{year}%"}).fetchall()   
        
         # ic| before_month: '2022-12
        before_month = get_date[0][0][:7]

        for x in range (0, len(get_date)):
            if before_month == get_date[x][0][:7]:
                hrs += get_date[x][1]
                mins += get_date[x][2]
                ic(f"{hrs}:{mins}")
                if get_date[x][0][5:7] not in existing_months:    
                    existing_months.append(get_date[x][0][5:7])
  
            else:   
                ic(f"{hrs}:{mins}")
                hr_and_mins_per_month.append((hrs + round(mins / 60)))
                hrs = 0 
                mins = 0
                ctr = x
                before_month = get_date[ctr][0][:7]

                # hr_and_mins_per_month: [8.6, 42.93, 69.03, 66.87, 0.78] - 0.78 should be 1.x

        ic(f"{hrs}:{mins}")
        hr_and_mins_per_month.append((hrs + round(mins / 60)))
        ic(hr_and_mins_per_month)
        #letter_format_months: ['August', 'September', 'October', 'November', 'December']
        letter_format_months = [calendar.month_name[int(num)] for num in existing_months]
        ic(letter_format_months, hr_and_mins_per_month)
        plt.figure(figsize=(10,7), dpi=120)
        plt.title(f'Total hours spend on {habit} per month', fontsize=18)
        plt.yticks(fontsize=14)
        plt.xticks(fontsize=14, rotation=45)

        ax1 = plt.gca()

        sns.barplot(x=letter_format_months, y=hr_and_mins_per_month, palette="rocket", ax=ax1)
        ax1.axhline(0, color="k", clip_on=False)
        ax1.set_ylabel("Hours")
        ax1.xaxis.label.set_color('Purple')   

        plt.show()
    
    else:
        return "1"

create_table()

# Date Dec 2 2022: database sum values

# From DB: 143:3089 = 194.48

# From graph: 8,6, 42.93, 69.03, 66.87, 0.78 = 188

# From graph without roundoff: 9, 43, 69, 67, 1 = 189