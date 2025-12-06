from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agile.db'
db = SQLAlchemy(app)

# -----------------------------
# Database Models
# -----------------------------
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(200))

class ScopeChange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer)
    change = db.Column(db.String(200))
    date = db.Column(db.String(20))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer)
    task_name = db.Column(db.String(100))
    status = db.Column(db.String(20))
    due_date = db.Column(db.String(20))
    priority = db.Column(db.String(10))  # High / Medium / Low

# -----------------------------
# Home Page Route
# -----------------------------
@app.route('/')
def index():
    projects = Project.query.all()
    changes = ScopeChange.query.all()
    tasks = Task.query.all()

    # Progress Report
    project_progress = {}
    for project in projects:
        total_tasks = Task.query.filter_by(project_id=project.id).count()
        done_tasks = Task.query.filter_by(project_id=project.id, status="Done").count()
        progress = round((done_tasks / total_tasks) * 100) if total_tasks else 0
        project_progress[project.id] = progress

    return render_template('index.html', projects=projects, changes=changes, tasks=tasks, progress=project_progress)

# -----------------------------
# Add Routes
# -----------------------------
@app.route('/add', methods=['POST'])
def add_project():
    name = request.form['name']
    description = request.form['description']
    new_project = Project(name=name, description=description)
    db.session.add(new_project)
    db.session.commit()
    return redirect('/')

@app.route('/add_change', methods=['POST'])
def add_change():
    project_id = request.form['project_id']
    change = request.form['change']
    date = request.form['date']
    new_change = ScopeChange(project_id=project_id, change=change, date=date)
    db.session.add(new_change)
    db.session.commit()
    return redirect('/')

@app.route('/add_task', methods=['POST'])
def add_task():
    project_id = request.form['project_id']
    task_name = request.form['task_name']
    status = request.form['status']
    due_date = request.form['due_date']
    priority = request.form['priority']
    new_task = Task(project_id=project_id, task_name=task_name, status=status, due_date=due_date, priority=priority)
    db.session.add(new_task)
    db.session.commit()
    return redirect('/')

# -----------------------------
# DELETE Routes
# -----------------------------
@app.route('/delete_project/<int:id>')
def delete_project(id):
    project = Project.query.get(id)
    db.session.delete(project)
    db.session.commit()
    return redirect('/')

@app.route('/delete_task/<int:id>')
def delete_task(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')

@app.route('/delete_change/<int:id>')
def delete_change(id):
    change = ScopeChange.query.get(id)
    db.session.delete(change)
    db.session.commit()
    return redirect('/')

# -----------------------------
# EDIT Routes (for Task only)
# -----------------------------
@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get(id)
    if request.method == 'POST':
        task.task_name = request.form['task_name']
        task.status = request.form['status']
        task.due_date = request.form['due_date']
        task.priority = request.form['priority']
        db.session.commit()
        return redirect('/')
    return render_template('edit_task.html', task=task)

# -----------------------------
# App Entry Point
# -----------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
