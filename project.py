from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Course

from flask import session as login_session
import random, string #python libraries

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2, json
import requests
from flask import make_response

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

#Connect to Database and create database session
engine = create_engine('sqlite:///cs_training.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Create a state token to prevent request
#Store it in the login_session for later validation
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in xrange(32))
    login_session['state'] = state
    return render_template('main.html', view = 'login', STATE = state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    #Check if request was sent from the right user
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter', 401))
        response.headers['Content-Type'] = 'application/json'
        return response
    
    code = request.data
    try:
        #Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #Check if the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    #If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    #Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match give user ID."), 401)  
        response.headers['Content-Type'] = 'application/json'
        return response

    #Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content_Type'] = 'application/json'
        return response

    #Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    store_gplus_id = login_session.get('gplus_id')
    if (stored_credentials is not None) and (gplus_id == store_gplus_id):
        response = make_response(json.dumps("Current user is already connected."), 200)
        response.headers['Content-Type'] = 'application/json'

    #Store the access token in the session for later use
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    #Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params = params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    output = ''
    output += '<div> Welcome, '+ login_session['username'] + '</div>'
    output += '<img src= "' + login_session['picture'] +'" alt="..." style="width: 200px; height:200px;">'
    output += '<div>'+ login_session['email'] +'</div>'
    return output


@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps("Current user not connected."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    #Execute HTTP GET to disconnect current token
    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    #Reset the user's session.
    del login_session['username']
    del login_session['picture']
    del login_session['email']
    del login_session['credentials']
    del login_session['gplus_id']
    if result['status'] == '200':
        response = make_response(json.dumps("Successfully disconnected."), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('getAllCategories'))
    else:
        response = make_response(json.dumps("Fail to disconnect."), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

#JSON APIs to view all categories
#@app.route('categories/JSON')
#def getAllCategoriesJSON():

#JSON APIs to view all courses of a category
#@app.route('categories/<int:category_id>/courses/JSON')

#Show all categories
@app.route('/')
@app.route('/categories')
def getAllCategories():
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return render_template('main.html', view='publicGetAllCategories', login_session=login_session, categories=categories)
    else:
        print 'login'
        return render_template('main.html', view='getAllCategories', login_session=login_session, categories=categories)


#Create a new category
@app.route('/categories/new', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        print "get here"
        return render_template('404.html')
    else:
        print login_session['username']
        if request.method == 'POST':
            if request.form['name']:
                categoryToAdd = Category(name = request.form['name'])
                session.add(categoryToAdd)
                session.commit()
            return redirect(url_for('getAllCategories'))
        else:    
            return render_template('main.html', view='newCategory', login_session=login_session)


#Edit a category
@app.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return render_template('404.html')
    else:
        categoryToEdit = session.query(Category).filter_by(id = category_id).one()
        if request.method == 'POST':
            if request.form['name']:
                categoryToEdit.name = request.form['name']
            session.add(categoryToEdit)
            session.commit()
            return redirect(url_for('getAllCategories'))
        return render_template('main.html', view='editCategory', login_session=login_session, category=categoryToEdit)

#Delete a category
@app.route('/categories/<int:category_id>/delete', methods=['GET','POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return render_template('404.html')
    else:
        categoryToDelete = session.query(Category).filter_by(id = category_id).one()
        coursesToDelete = session.query(Course).filter_by(category_id = category_id).all()
        if request.method == 'POST':
            for c in coursesToDelete:
                session.delete(c)
            session.delete(categoryToDelete)
            session.commit()
            return redirect(url_for('getAllCategories'))
        else:
            return render_template('main.html', view='deleteCategory', login_session=login_session, category=categoryToDelete)


#Show all courses of a given category
@app.route('/categories/<int:category_id>/courses')
def getCoursesByCategoryId(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    courses = session.query(Course).filter_by(category_id = category_id).all()
    if 'username' not in login_session:
        return render_template('main.html', view='publicGetCoursesByCategoryId', login_session=login_session, category=category, courses=courses)
    else:
        return render_template('main.html', 'getCoursesByCategoryId', login_session=login_session, category=category, courses=courses)


#Create a new course for a given category
@app.route('/categories/<int:category_id>/courses/new', methods=['GET', 'POST'])
def newCourse(category_id):
    if 'username' not in login_session:
        return render_template('404.html')
    else:
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
            return render_template('main.html', view='newCourse', login_session=login_session, category = category)


#Edit a course
@app.route('/categories/<int:category_id>/courses/<int:course_id>/edit', methods=['GET', 'POST'])
def editCourse(category_id, course_id):
    if 'username' not in login_session:
        return render_template('404.html')
    else:
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
            return redirect(url_for('getCoursesByCategoryId', category_id=category_id, course_id=course_id))
        else:
            return render_template('main.html', view='editCourse', login_session=login_session, category=category, course=courseToEdit)


#Delete a course
@app.route('/categories/<int:category_id>/courses/<int:course_id>/delete', methods=['GET', 'POST'])
def deleteCourse(category_id, course_id):
    if 'username' not in login_session:
        return render_template('404.html')
    else:
        category = session.query(Category).filter_by(id = category_id).one()
        courseToDelete = session.query(Course).filter_by(id = course_id, category_id = category_id).one()
        if request.method == 'POST':
            session.delete(courseToDelete)
            session.commit()
            return redirect(url_for('getCoursesByCategoryId', category_id = category_id, course_id = course_id))
        else:
            return render_template('main.html', view='deleteCourse', login_session=login_session, category=category, course=courseToDelete)


#Show a course
@app.route('/categories/<int:category_id>/courses/<int:course_id>')
def getCourseById(category_id, course_id):
    category = session.query(Category).filter_by(id = category_id).one()
    course = session.query(Course).filter_by(id = course_id, category_id = category_id).one()
    return render_template('main.html', view='getCourseById', login_session=login_session, category = category, course = course)


#Set the secret key
app.secret_key = 'P\xb1\x97\ry(\xb4\xcc\x10\xd2\x9d\xc7\xc1\xaf2\x8f,\xac*\x98H\xdbi\xe7'

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
