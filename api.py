from logging import debug
from flask import Flask
from flask_restful import Resource, Api, abort, reqparse
from flask_cors import CORS
import json
from datetime import datetime
from os import path
from colors import Colors
import logging

app = Flask("JSON server")
CORS(app, resources={r"/*": {"origin": "*"}})
api = Api(app)


logging.getLogger('flask_cors').level = logging.DEBUG

parser = reqparse.RequestParser()
parser.add_argument('id', required=True, type=int)
parser.add_argument('text', required=True)
parser.add_argument('day', required=True)
parser.add_argument('reminder', required=True, type=bool)


def create_db():
    """ creates db.json if it doesn't exists else skips"""
    if path.exists("./db.json"):
        print(Colors.CYAN, "\ndb.json exists\n", Colors.WHITE)
    else:
        print(
            Colors.RED, "\nWARNING: db.json doesn't exists. Creating now...\n", Colors.WHITE)
        with open("./db.json", 'w') as file:
            json.dump({"tasks": []}, file)
        print(Colors.GREEN, "db.json created successfully\n", Colors.WHITE)


create_db()


def get_all_tasks_data():
    """ returns all the current data in the db.json file"""
    with open('./db.json', 'r') as db:
        return json.load(db)


def save(data):
    '''writes @param:data to db.json '''
    with open('./db.json', 'w') as db:
        json.dump(data, db)


def add_new_task_data(new_data):
    """ adds the new tasks to db.json"""
    existing_data = get_all_tasks_data()
    with open('./db.json', 'w') as db:
        existing_data['tasks'].append(new_data)
        save(existing_data)


def yield_tasks():
    """ generator that yields data """
    tasks = get_all_tasks_data()
    for task in tasks['tasks']:
        yield task


def get_task(task_id: int):
    """ returns the task with task_id s"""
    for task in yield_tasks():
        if task['id'] == task_id:
            return task


def get_task_index(task_id: int):
    """ get the index of the task with task_id"""
    tasks = get_all_tasks_data()['tasks']
    return tasks.index(get_task(task_id))


def parse_date(date):
    """ parse time to proper format of [abbrev. weekday, abbrev. Month day year] """
    date = list(map(int, date.split("-")))
    dt = datetime(date[0], date[1], date[2])
    parsed_date = dt.strftime("%a, %b %d %Y")

    return parsed_date


def abort_if_task_doesnt_exist(task_id: int):
    """ returns error 404 if the task doesn't exist """
    task = get_task(task_id)
    if task is None:
        abort(404, message=f"Task with id {task_id} doesn't exist")


class TasksList(Resource):
    """ TASKS LIST """

    def get(self):
        return get_all_tasks_data(), 200

    def post(self):
        args = parser.parse_args()
        args['day'] = parse_date(args['day'])
        add_new_task_data(args)

        return "", 201


class Tasks(Resource):
    def get(self, task_id):
        abort_if_task_doesnt_exist(task_id)
        data = get_task(task_id)
        return data, 200

    def put(self, task_id):
        abort_if_task_doesnt_exist(task_id)
        # parse: args = data in JSON/dict format
        args = parser.parse_args()

        task_idx = get_task_index(task_id)
        all_tasks = get_all_tasks_data()

        # update the task
        all_tasks['tasks'][task_idx].update(args)

        # save data with an updated task
        save(all_tasks)
        return all_tasks['tasks'][task_idx]

    def delete(self, task_id):
        abort_if_task_doesnt_exist(task_id)
        task_idx = get_task_index(task_id)
        all_tasks = get_all_tasks_data()
        all_tasks['tasks'].pop(task_idx)
        save(all_tasks)

        return 204


api.add_resource(TasksList, '/tasks')
api.add_resource(Tasks, "/tasks/<int:task_id>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
