# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
import json

# configuration (could also be in external file...see below)
DATABASE = 'flaskr.json'
DEBUG = True
SECRET_KEY = 'secretkey'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)


# get configuration details (either from this or external file)
#app.config.from_object(__name__)

# Set this environment variable using export FLASKR_SETTINGS=....
#FLASKR_SETTINGS = '/Users/mike/SkyDrive/Personal/Education/flask/flaskr/FLASKR_SETTINGS.ini'
app.config.from_envvar('FLASKR_SETTINGS', silent=False)


@app.before_request
def before_request():
    try:
        db = open(DATABASE).read()
    except IOError:
    	db = '{"entries":[]}'
    g.db = json.loads(db)

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        open(DATABASE, 'w').write(json.dumps(g.db))

@app.route('/')
def show_entries():
	return render_template('show_entries.html', entries=g.db['entries'])

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	g.db['entries'].insert(0, {'title': request.form['title'], 'text': request.form['text']})
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

if __name__ == '__main__':
	app.run()
