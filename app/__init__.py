from flask import Flask, redirect, url_for

app = Flask(__name__)

from app.controllers import auth_controller
app.register_blueprint(blueprint=auth_controller.auth_ctrl, url_prefix='/auth')

from app.controllers import category_controller
app.register_blueprint(blueprint=category_controller.category_ctrl, url_prefix='/categories')

from app.controllers import course_controller
app.register_blueprint(blueprint=course_controller.course_ctrl, url_prefix='')


@app.route('/')
def homepage():
    return redirect(url_for('category.get_all_categories'))
