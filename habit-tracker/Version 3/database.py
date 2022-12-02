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
        # get_date len 121 - Dec 1 2022
        
        # Convert the extraced date from date_added then convert it to datetime format: Date format example: 2018-12-31
        to_date = [datetime.strptime(get_date[x][0], "%Y-%m-%d").date() for x in range(0, len(get_date))]
        
        # ic(to_date) - matches current index

        # Seperating month, day and summing up hours and mins.
        for x in range(0, len(get_date)):

            # Checks the date_added table if that month is not in the unq_mths list.
            if to_date[x].month not in unq_mths:
                
                unq_mths.append(to_date[x].month)
                # ic(unq_mths) shows a list of [8 to 12] = 5
                # Categorize the to_date dates to their category.
                yr.append(to_date[x].year)
                mths.append(to_date[x].month)
                day.append(to_date[x].day)

        # If inputted year does not exist yet return error msg.
        if len(unq_mths) <= 1 or year not in yr:
                return "1"

       
        while ctr != len(unq_mths):         
            
            
            # Insert the first month of the to_date list to before_month.
            before_month = to_date[ctr].month
            ic(before_month) # outputs all 8 two times.
            # ic(f"seperating values: {len(to_date)}")  121 output

            # Iterate every rows / ctr2 default value is 0
            for z in range(ctr2, len(get_date)):
                
                # Check if the to_date month value matches the before_month value
                if int(to_date[z].month) == before_month:
                    # If true then put mins and hour in their respective list
                    mins.append(get_date[z][2])
                    hrs.append(get_date[z][1])
                    
                    # Divided the mns list total to 60 and append the value to_hrs list
                    if sum(mins) > 60:
                        to_hrs = round((sum(mins) / 60), 2)
                             

                # If iterated new month is not the same as the before montth change the value of before_month to new recent iterated month
                elif int(to_date[z].month) != before_month:
                    total_hrs_per_month.append(to_hrs + sum(hrs))

                    # TOD0: Dec 1 2022 current problem is index stops at 118 and does not continue to 121
                    ic(f"It stops from {z} - ") 
                    before_month = int(to_date[z].month)  
                    # ctr2 will save the last iterated row so hrs and mins from different month will not be saved from the first month     
                    ctr2 = z
                    # ctr will change the value of the before_month to the index 1 on the list
                    ctr += 1
                    ic(f"{unq_mths}, {ctr}")
                    # clear the hrs, mins and to_hrs to make way for new values for the new month to be calculated.
                    mins.clear()
                    hrs.clear()
                    to_hrs = 0

        # Output is correct :- 
        months_in_names = [calendar.month_name[num] for num in unq_mths]
        ic(months_in_names)

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
   
        


create_table()