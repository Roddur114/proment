from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    product_type = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.String(20), nullable=False)  # Rating as a text field
    members = db.Column(db.String(200), nullable=False)
    progress = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')
    
    if order == 'asc':
        projects = Project.query.order_by(asc(getattr(Project, sort_by))).all()
    else:
        projects = Project.query.order_by(desc(getattr(Project, sort_by))).all()
    
    return render_template('index.html', projects=projects, sort_by=sort_by, order=order)

@app.route('/add_project', methods=['POST'])
def add_project():
    name = request.form.get('name')
    product_type = request.form.get('product_type')
    rating = request.form.get('rating')
    members = request.form.get('members')
    progress = 'In Progress'  # Set default status to "In Progress"

    if name and product_type and rating and members:
        new_project = Project(name=name, product_type=product_type, rating=rating, members=members, progress=progress)
        db.session.add(new_project)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project.name = request.form.get('name')
        project.product_type = request.form.get('product_type')
        project.rating = request.form.get('rating')
        project.members = request.form.get('members')
        project.progress = request.form.get('progress')
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('edit_project.html', project=project)

@app.route('/update_project/<int:project_id>', methods=['POST'])
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    new_progress = request.form.get('progress')
    
    if new_progress in ['In Progress', 'Finished']:
        project.progress = new_progress
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/api/projects', methods=['GET'])
def api_projects():
    projects = Project.query.all()
    return jsonify([{
        'id': project.id,
        'name': project.name,
        'product_type': project.product_type,
        'rating': project.rating,
        'members': project.members,
        'progress': project.progress
    } for project in projects])

if __name__ == '__main__':
    app.run(debug=True)
    