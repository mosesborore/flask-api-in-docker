from flask import Flask, jsonify, redirect
from flask_restful import Resource, Api, abort, reqparse
from flask_cors import CORS
import json
from datetime import datetime
from os import path
from colors import Colors
import logging
from flask_sqlalchemy import SQLAlchemy


app = Flask("JSON server")

# setup database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# setup CORS
CORS(app, resources={r"/*": {"origin": "*"}})

# setup api
api = Api(app)


# Modelling
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250), nullable=False)
    day = db.Column(db.String(100), nullable=False)
    reminder = db.Column(db.Boolean, nullable=False, default=False)

    def __str__(self):
        return str(f"Task {self.id}")


def create_db():
    """creates database.db if it doesn't exists else skips"""
    if path.exists("./database.db"):
        print(Colors.CYAN, "\ndatabase.db exists\n", Colors.WHITE)
    else:
        print(
            Colors.RED,
            "\nWARNING: database.db doesn't exists. Creating now...\n",
            Colors.WHITE,
        )
        db.create_all()
        print(Colors.GREEN, "database.db created successfully\n", Colors.WHITE)


create_db()

logging.getLogger("flask_cors").level = logging.DEBUG

# setting up request argument parser
parser = reqparse.RequestParser()
parser.add_argument("id", required=True, type=int)
parser.add_argument("text", required=True)
parser.add_argument("day", required=True)
parser.add_argument("reminder", required=True, type=bool)


def parse_date(date):
    """parse time to proper format of [abbrev. weekday, abbrev. Month day year]"""
    date, time = date.split("T")
    date = list(map(int, date.split("-")))
    dt = datetime(date[0], date[1], date[2])
    parsed_date = dt.strftime("%a, %b %d") + f" {time}"

    return parsed_date


def get_task(task_id: int):
    """returns the task with task_id"""
    task = Task.query.get(task_id)
    data = {
        "id": task.id,
        "text": task.text,
        "day": task.day,
        "reminder": task.reminder,
    }
    return data


def abort_if_task_doesnt_exist(task_id: int):
    """returns error 404 if the task with 'task_id' doesn't exist"""
    task = Task.query.filter_by(id=task_id).first_or_404(
        description=f"task with {task_id} doesn't exist"
    )
    if task is None:
        abort(404, message=f"Task with id {task_id} doesn't exist")


class TasksList(Resource):
    """TASKS LIST"""

    def get(self):
        tasks = Task.query.all()
        data = {"tasks": []}

        for task in tasks:
            current = {
                "id": task.id,
                "text": task.text,
                "day": task.day,
                "reminder": task.reminder,
            }
            data["tasks"].append(current)

        return data, 200

    def post(self):
        args = parser.parse_args()
        # parse date and time
        args["day"] = parse_date(args["day"])

        # create new Task
        new_task = Task(
            id=args["id"], text=args["text"], day=args["day"], reminder=args["reminder"]
        )

        db.session.add(new_task)
        db.session.commit()

        return "", 201


class Tasks(Resource):
    def get(self, task_id):
        abort_if_task_doesnt_exist(task_id)
        task = get_task(task_id)
        return task, 200

    def put(self, task_id):
        abort_if_task_doesnt_exist(task_id)
        # parse: args = data in JSON/dict format
        args = parser.parse_args()
        task = Task.query.get(task_id)

        task.reminder = args["reminder"]
        # commit changes
        db.session.commit()

        return get_task(task_id)

    def delete(self, task_id):
        abort_if_task_doesnt_exist(task_id)
        task = Task.query.get(task_id)
        db.session.delete(task)
        db.session.commit()

        return 204


class TaskRedirect(Resource):
    def get(self):
        return redirect("/tasks")


api.add_resource(TaskRedirect, "/")
api.add_resource(TasksList, "/tasks")
api.add_resource(Tasks, "/tasks/<int:task_id>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
