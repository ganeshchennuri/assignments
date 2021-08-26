from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from models import Task
from schema import task_schema, tasks_schema

app = Flask(__name__)

auth = HTTPBasicAuth()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config ['JSON_SORT_KEYS'] = False

users = {
    "logic": generate_password_hash("loop"),
    "digital": generate_password_hash("marketing")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@app.before_first_request   #This method will run before the first request is sent & Create all tables if not created
def create_tables():
    db.create_all() 

class ToDo(MethodView):
    @auth.login_required
    def get(self, task_id):
        if task_id is None:
            tasks = Task.query.all()
            return tasks_schema.jsonify(tasks),200
        else:
            task = Task.query.filter_by(id=task_id).first()
            if not task:
                return jsonify({"message": f"Task with id {task_id} Not Found"}),404
            return task_schema.jsonify(task),200

    @auth.login_required
    def post(self):
        try:
            data = request.get_json()
            task = Task(title = data.get('title'),description = data.get('description'), done = data.get('done',False))
        except:
            return jsonify({"message": "Error in payload, provide title, description in json Format"}),400
        task.save_to_db()
        return task_schema.jsonify(task),201

    @auth.login_required
    def delete(self, task_id):
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return jsonify({"message": f"task with id {task_id} not found"}),404
        task.delete_from_db()
        return jsonify({"message": "task deleted"}),200

    @auth.login_required
    def put(self, task_id):
        task = Task.query.filter_by(id=task_id).first()

        if not task:
            return jsonify({"message": f"Task with id {task_id} Not Found"}),404

        try:
            data = request.get_json()
            task.title = data.get('title', task.title)
            task.description = data.get('description', task.description)
            task.done = data.get('done',task.done)
        except:
            return jsonify({"message": "Error in payload, provide title, description, done in json Format"}),400

        task.save_to_db()
        return task_schema.jsonify(task),200
        

todo_view = ToDo.as_view('todo_view')

app.add_url_rule('/todo/api/v1.0/tasks/', view_func=todo_view, methods=['POST',])
app.add_url_rule('/todo/api/v1.0/tasks/', defaults={'task_id': None},
                 view_func=todo_view, methods=['GET',])
app.add_url_rule('/todo/api/v1.0/tasks/<int:task_id>', view_func=todo_view,
                 methods=['GET', 'PUT', 'DELETE'])

if __name__ == "__main__":
    from db import db
    from ma import ma
    db.init_app(app)
    ma.init_app(app)
    app.run(debug=True)