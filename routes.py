from flask import  Blueprint,render_template, request, redirect, url_for
import datetime
from collections import defaultdict
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

pages = Blueprint("habits", __name__, template_folder="template", static_folder="static")

#habits = ["Test Habit", "Second Habit"]
#completions = defaultdict(list)
MONGO_URL = os.environ.get("MONGO_URL")
mongo_client= MongoClient(MONGO_URL)
db = mongo_client["habit_tracker"]
habits = db["habits"]
completions = db['completions']


@pages.context_processor
def add_date_range():
    def date_range(start):
        dates = [start+ datetime.timedelta(days=diff) for diff in range(-3,4)] 
        return dates
    return {"date_range":date_range}



@pages.route('/')
def index():
    date = request.args.get("date")

    if date:
        selected_date = datetime.date.fromisoformat(date) 
    else:
        selected_date = datetime.date.today()

    habits_contents = [habit["habit"] for habit in habits.find({})]
    completions_content = [completion["habit"] for completion in completions.find({"date":datetime.datetime.combine(selected_date,datetime.time())})]

    return render_template("index.html", habits = habits_contents ,title = "Habit Tracker - Home", selected_date=selected_date, completions=completions_content)

@pages.route("/add", methods=["POST","GET"])
def add_habit():

    if request.method == "POST":    
        habit = request.form.get("habit")
        #habits.append(habit)
        habits.insert_one({"habit":habit})

        return redirect(url_for("habits.index", date= datetime.date.today()))
    else:
        return render_template("add_habit.html", title = "Habit Tracker - Add Habit", selected_date=datetime.date.today())


@pages.route("/complete", methods = ["POST"])
def complete():
    date_string  = request.form.get("date")
    habit  = request.form.get("habitName")
    date = datetime.date.fromisoformat(date_string)
    #completions[date].append(habit)
    completions.insert_one({"date":datetime.datetime.combine(date,datetime.time()), "habit":habit})
    return redirect(url_for("habits.index", date= date_string))
