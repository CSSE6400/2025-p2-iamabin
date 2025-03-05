from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime
from datetime import datetime, timedelta
api = Blueprint('api', __name__, url_prefix='/api/v1')
ALLOWED_TEXT = {'title', 'description', 'completed', 'deadline_at'}

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    query = Todo.query

    completed_param = request.args.get('completed')
    if completed_param is not None:
        completed = completed_param.lower() == 'true'
        query = query.filter_by(completed=completed)


    window_param = request.args.get('window')
    if window_param:
        try:
            window_days = int(window_param)
            deadline_limit = datetime.now() + timedelta(days=window_days)
            query = query.filter(Todo.deadline_at <= deadline_limit)
        except ValueError:
            return jsonify({'error': 'Invalid window parameter'}), 400

    todos = query.all()
    return jsonify([todo.to_dict() for todo in todos])


@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())




@api.route('/todos', methods=['POST'])
def create_todo():

    extra_fields = set(request.json.keys()) - ALLOWED_TEXT
    if extra_fields:
        return jsonify({'error': f'Invalid fields: {extra_fields}'}), 400

    title = request.json.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    title = request.json.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
        # Adds a new record to the database or will update an existing record.
    db.session.add(todo)
    # Commits the changes to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    extra_fields = set(request.json.keys()) - ALLOWED_TEXT
    if extra_fields:
        return jsonify({'error': f'Invalid fields: {extra_fields}'}), 400
    if 'id' in request.json:
        return jsonify({'error': 'ID cannot be modified'}), 400
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()
    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
 
