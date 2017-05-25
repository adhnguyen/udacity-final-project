import os
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Course

engine = create_engine('sqlite:///cs_training.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

'''
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
'''

@app.route('/')
@app.route('/categories/')
def getAllCategories():
    categories = session.query(Category).all()
    return render_template('getAllCategories.html', categories = categories)

@app.route('/categories/new', methods=['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        categoryToAdd = Category(name = request.form['name'])
        session.add(categoryToAdd)
        session.commit()
        return redirect(url_for('getAllCategories'))
    else:    
        return render_template('newCategory.html')


@app.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    categoryToEdit = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            categoryToEdit.name = request.form['name']
        session.add(categoryToEdit)
        session.commit()
        return redirect(url_for('getAllCategories'))
    return render_template('editCategory.html', category = categoryToEdit)


@app.route('/categories/<int:category_id>/delete', methods=['GET','POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(Category).filter_by(id = category_id).one()
    coursesToDelete = session.query(Course).filter_by(category_id = category_id).all()
    if request.method == 'POST':
        for c in coursesToDelete:
            session.delete(c)
        session.delete(categoryToDelete)
        session.commit()
        return redirect(url_for('getAllCategories'))
    else:
        return render_template('deleteCategory.html', category = categoryToDelete)


@app.route('/categories/<int:category_id>/courses')
def getCoursesByCategoryId(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    courses = session.query(Course).filter_by(category_id = category_id).all()
    return render_template('getCoursesByCategoryId.html', category = category, courses = courses)


@app.route('/categories/<int:category_id>/courses/new', methods=['GET', 'POST'])
def newCourse(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            courseToAdd = Course(
                name = request.form['name'], 
                description = request.form['description'], 
                img_url = request.form['img-url'], 
                intro_video_url = request.form['intro-video-url'], 
                category_id = category_id)
        session.add(courseToAdd)
        session.commit()
        return redirect(url_for('getCoursesByCategoryId', category_id = category_id))
    else:
        return render_template('newCourse.html', category = category)


@app.route('/categories/<int:category_id>/courses/<int:course_id>')
def getCourseById(category_id, course_id):
    category = session.query(Category).filter_by(id = category_id).one()
    course = session.query(Course).filter_by(id = course_id, category_id = category_id).one()
    print ("course: " + str(course))
    return render_template('getCourseById.html', category = category, course = course)


@app.route('/categories/<int:category_id>/courses/<int:course_id>/edit', methods=['GET', 'POST'])
def editCourse(category_id, course_id):
    category = session.query(Category).filter_by(id = category_id).one()
    courseToEdit = session.query(Course).filter_by(id = course_id, category_id = category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            courseToEdit.name = request.form['name']
            courseToEdit.description = request.form['description']
            courseToEdit.img_url = request.form['img-url']
            courseToEdit.intro_video_url = request.form['intro-video-url']
        session.add(courseToEdit)
        session.commit()
        return redirect(url_for('getCourseById', category_id = category_id, course_id = course_id))
    else:
        return render_template('editCourse.html', category = category, course = courseToEdit)


@app.route('/categories/<int:category_id>/courses/<int:course_id>/delete', methods=['GET', 'POST'])
def deleteCourse(category_id, course_id):
    print category_id, course_id
    category = session.query(Category).filter_by(id = category_id).one()
    courseToDelete = session.query(Course).filter_by(id = course_id, category_id = category_id).one()
    print courseToDelete
    if request.method == 'POST':
        session.delete(courseToDelete)
        session.commit()
        return redirect(url_for('getCoursesByCategoryId', category_id = category_id, course_id = course_id))
    else:
        return render_template('deleteCourse.html', category = category, course = courseToDelete)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
