#----------------------------------------------------------------------- Imports

from flask import render_template, url_for, flash, redirect
from momentum_flask import app # type: ignore
#from flaskblog.forms import RegistrationForm, LoginForm
from momentum_flask.models import User, Project, Time_Entry, Task_Entry # type: ignore

#----------------------------------------------------------------------- GENERAL FUNCTIONS

#----------------------------------------------------------------------- PAGE CODE

@app.route('/') 
def home():
    return redirect(url_for('landing'))

@app.route('/landing') 
def landing():
    return render_template(
        "landing.html",
        title='Momentum'
        )

@app.route('/dashboard') 
def dashboard():
    return render_template(
        "dashboard.html",
        title='Dashboard'
        )