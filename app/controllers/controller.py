import json
import random
import string

import httplib2
import requests
from flask import (
    Flask,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for
)
from flask import session as login_session
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from app.models import Base, Category, Course
from app.models.category_model import Category
from app.models.course_model import Course
from app.database import session

app = Flask(__name__)

""" # Connect to Database and create database session
engine = create_engine('sqlite:///cs_training.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
"""
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


# Create a state token to prevent request
# Store it in the login_session for later validation
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('_main.html', view='login', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Check if request was sent from the right user
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter', 401))
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match give user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content_Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    store_gplus_id = login_session.get('gplus_id')
    if (stored_credentials is not None) and (gplus_id == store_gplus_id):
        response = make_response(json.dumps("Current user is already connected."), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    output = ''
    output += '<div> Welcome, <span class="title-bold">' + login_session['username'] + '</span></div>'
    output += '<img src= "' + login_session['picture'] \
              + '" alt="..." ' \
                'style="width: 150px; height:150px; border-radius: 75px; border: 3px solid #000; margin: 15px;">'
    output += '<div>' + login_session['email'] + '</div>'
    return output


@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps("Current user not connected."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET to disconnect current token
    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # Reset the user's session.
    del login_session['username']
    del login_session['picture']
    del login_session['email']
    del login_session['credentials']
    del login_session['gplus_id']
    if result['status'] == '200':
        response = make_response(json.dumps("Successfully disconnected."), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('get_all_categories'))
    else:
        response = make_response(json.dumps("Fail to disconnect."), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view all categories
@app.route('/categories/JSON')
def get_all_categories_JSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


# JSON APIs to view all courses of a category
@app.route('/categories/<int:category_id>/courses/JSON')
def get_courses_by_categoryID_JSON(category_id):
    courses = session.query(Course).filter_by(category_id=category_id).all()
    return jsonify(CoursesList=[c.serialize for c in courses])


# Show all categories
@app.route('/')
@app.route('/categories')
def get_all_categories():
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return render_template('_main.html', view='public_get_all_categories',
                               login_session=login_session, categories=categories)
    else:
        return render_template('_main.html', view='get_all_categories',
                               login_session=login_session, categories=categories)


# Create a new category
@app.route('/categories/new', methods=['GET', 'POST'])
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
                return redirect(url_for('get_all_categories'))
            else:
                flash('Category name is required.', 'error')
                return render_template('_main.html', view='new_category', login_session=login_session)
        else:
            return render_template('_main.html', view='new_category', login_session=login_session)


# Edit a category
@app.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
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
                return redirect(url_for('get_all_categories'))
            else:
                flash('Category name is required.', 'error')
                return render_template('_main.html', view='edit_category',
                                       login_session=login_session, category=category)
        return render_template('_main.html', view='edit_category',
                               login_session=login_session, category=category)


# Delete a category
@app.route('/categories/<int:category_id>/delete', methods=['GET', 'POST'])
def delete_category(category_id):
    if 'username' not in login_session:
        return render_template('404.html')
    else:
        try:
            category = session.query(Category).filter_by(id=category_id).one()
            tmp = category.name
        except:
            return render_template('404.html')

        courses = session.query(Course).filter_by(category_id=category_id).all()
        if request.method == 'POST':
            for course in courses:
                session.delete(course)
            session.delete(category)
            session.commit()
            flash('Successfully deleted the "' + tmp + '" category and all of its sub-courses.')
            return redirect(url_for('get_all_categories'))
        else:
            return render_template('_main.html', view='delete_category',
                                   login_session=login_session, category=category)


# Show all courses of a given category
@app.route('/categories/<int:category_id>/courses')
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
@app.route('/categories/<int:category_id>/courses/new', methods=['GET', 'POST'])
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
                return redirect(url_for('get_courses_by_categoryID', category_id=category_id))
            else:
                flash('Course name is required.', 'error')
                return render_template('_main.html', view='new_course',
                                       login_session=login_session, category=category)
        else:
            return render_template('_main.html', view='new_course',
                                   login_session=login_session, category=category)


# Edit a course
@app.route('/categories/<int:category_id>/courses/<int:course_id>/edit', methods=['GET', 'POST'])
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
                return redirect(url_for('get_courses_by_categoryID', category_id=category_id, course_id=course_id))
            else:
                flash('Course name is required.', 'error')
                return render_template('_main.html', view='edit_course',
                                       login_session=login_session, category=category, course=course)
        else:
            return render_template('_main.html', view='edit_course',
                                   login_session=login_session, category=category, course=course)


# Delete a course
@app.route('/categories/<int:category_id>/courses/<int:course_id>/delete', methods=['GET', 'POST'])
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
            return redirect(url_for('get_courses_by_categoryID', category_id=category_id, course_id=course_id))
        else:
            return render_template('_main.html', view='delete_course',
                                   login_session=login_session, category=category, course=course)


# Show a course
@app.route('/categories/<int:category_id>/courses/<int:course_id>')
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