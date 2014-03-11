"""
    Public views for the website, not related
    to the functionality.Include views such as
    the homepage, about, contact, etc.
"""
from flask import render_template
from codeta import app

@app.route('/')
def homepage():
    return render_template('codeta/home.html')

@app.route('/about')
def about():
    return render_template('user/about.html')

@app.route('/support')
def support():
    return render_template('user/support.html')

@app.route('/contact')
def contact():
    return render_template('user/contact.html')
