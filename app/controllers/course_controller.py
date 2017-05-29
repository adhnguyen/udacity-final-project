from app.database import session

from app.controllers.auth_controller import login_session
from app.models.category_model import Category
from app.models.course_model import Course

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

course_ctrl = Blueprint('course', __name__, static_folder='static', template_folder='templates')


# Show all courses of a given category
@course_ctrl.route('/categories/<int:category_id>/courses')
def get_courses_by_categoryID(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        flash('Invalid category.', 'error')
        return render_template('404.html')

    courses = session.query(Course).filter_by(category_id=category_id).all()
    if 'username' not in login_session:
        return render_template('_main.html', view='public_get_courses_by_categoryID',
                               login_session=login_session, category=category, courses=courses)
    else:
        return render_template('_main.html', view='get_courses_by_categoryID',
                               login_session=login_session, category=category, courses=courses)


# Create a new course for a given category
@course_ctrl.route('/categories/<int:category_id>/courses/new', methods=['GET', 'POST'])
def new_course(category_id):
    if 'username' not in login_session:
        return render_template('404.html')
    else:
        try:
            category = session.query(Category).filter_by(id=category_id).one()
        except:
            return render_template('404.html')

        if request.method == 'POST':
            if request.form['name']:
                course = Course(name=request.form['name'],
                                description=request.form['description'],
                                img_url=request.form['img-url'],
                                intro_video_url=request.form['intro-video-url'],
                                category_id=category_id)
                flash('Successfully added the new course.')
                session.add(course)
                session.commit()
                return redirect(url_for('course.get_courses_by_categoryID', category_id=category_id))
            else:
                flash('Course name is required.', 'error')
                return render_template('_main.html', view='new_course',
                                       login_session=login_session, category=category)
        else:
            return render_template('_main.html', view='new_course',
                                   login_session=login_session, category=category)


# Edit a course
@course_ctrl.route('/categories/<int:category_id>/courses/<int:course_id>/edit', methods=['GET', 'POST'])
def edit_course(category_id, course_id):
    if 'username' not in login_session:
        return render_template('404.html')
    else:
        try:
            category = session.query(Category).filter_by(id=category_id).one()
            course = session.query(Course).filter_by(id=course_id, category_id=category_id).one()
        except:
            return render_template('404.html')

        if request.method == 'POST':
            if request.form['name']:
                course.name = request.form['name']
                course.description = request.form['description']
                course.img_url = request.form['img-url']
                course.intro_video_url = request.form['intro-video-url']
                session.add(course)
                session.commit()
                flash('Successfully edited the course profile.')
                return redirect(url_for('course.get_courses_by_categoryID', category_id=category_id, course_id=course_id))
            else:
                flash('Course name is required.', 'error')
                return render_template('_main.html', view='edit_course',
                                       login_session=login_session, category=category, course=course)
        else:
            return render_template('_main.html', view='edit_course',
                                   login_session=login_session, category=category, course=course)


# Delete a course
@course_ctrl.route('/categories/<int:category_id>/courses/<int:course_id>/delete', methods=['GET', 'POST'])
def delete_course(category_id, course_id):
    if 'username' not in login_session:
        return render_template('404.html')
    else:
        try:
            category = session.query(Category).filter_by(id=category_id).one()
            course = session.query(Course).filter_by(id=course_id, category_id=category_id).one()
        except:
            return render_template('404.html')

        if request.method == 'POST':
            session.delete(course)
            session.commit()
            flash('Successfully deleted the course "' + course.name + '".')
            return redirect(url_for('course.get_courses_by_categoryID', category_id=category_id, course_id=course_id))
        else:
            return render_template('_main.html', view='delete_course',
                                   login_session=login_session, category=category, course=course)


# Show a course
@course_ctrl.route('/categories/<int:category_id>/courses/<int:course_id>')
def get_course_by_id(category_id, course_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except:
        flash('Invalid category.', 'error')
        return render_template('404.html')
    try:
        course = session.query(Course).filter_by(id=course_id, category_id=category_id).one()
    except:
        flash('Invalid course.', 'error')
        return render_template('404.html')

    return render_template('_main.html', view='get_course_by_id',
                           login_session=login_session, category=category, course=course)