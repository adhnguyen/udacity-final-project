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

category_ctrl = Blueprint('category', __name__, static_folder='static', template_folder='templates')


# Show all categories
@category_ctrl.route('/')
def get_all_categories():
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return render_template('_main.html', view='public_get_all_categories',
                               login_session=login_session, categories=categories)
    else:
        print 'login'
        return render_template('_main.html', view='get_all_categories',
                               login_session=login_session, categories=categories)


# Create a new category
@category_ctrl.route('/new', methods=['GET', 'POST'])
def new_category():
    if 'username' not in login_session:
        return render_template('404.html')
    else:
        print login_session['username']
        if request.method == 'POST':
            if request.form['name']:
                category = Category(name=request.form['name'])
                session.add(category)
                session.commit()
                flash('Successfully added the new category.')
                return redirect(url_for('category.get_all_categories'))
            else:
                flash('Category name is required.', 'error')
                return render_template('_main.html', view='new_category', login_session=login_session)
        else:
            return render_template('_main.html', view='new_category', login_session=login_session)


# Edit a category
@category_ctrl.route('/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    if 'username' not in login_session:
        return render_template('404.html')
    else:
        try:
            category = session.query(Category).filter_by(id=category_id).one()
        except:
            return render_template('404.html')

        if request.method == 'POST':
            if request.form['name']:
                category.name = request.form['name']
                session.add(category)
                session.commit()
                flash('Successfully edited the category.')
                return redirect(url_for('category.get_all_categories'))
            else:
                flash('Category name is required.', 'error')
                return render_template('_main.html', view='edit_category',
                                       login_session=login_session, category=category)
        return render_template('_main.html', view='edit_category',
                               login_session=login_session, category=category)


# Delete a category
@category_ctrl.route('/<int:category_id>/delete', methods=['GET', 'POST'])
def delete_category(category_id):
    if 'username' not in login_session:
        return render_template('404.html')
    else:
        try:
            category = session.query(Category).filter_by(id=category_id).one()
            tmp = category.name
        except:
            return render_template('404.html')

        if request.method == 'POST':
            session.delete(Course).filter_by(category_id=category_id).all()
            session.delete(category)
            session.commit()
            flash('Successfully deleted the "' + tmp + '" category and all of its sub-courses.')
            return redirect(url_for('category.get_all_categories'))
        else:
            return render_template('_main.html', view='delete_category',
                                   login_session=login_session, category=category)
