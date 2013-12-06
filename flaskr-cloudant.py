# all the imports
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import time
import cloudant
import logging

# configuration (could also be in external file...see below)
# Create a database called DATABASE in your ACCOUNT.cloudant.com and make it world-writeable
ACCOUNT = 'michaelbreslin'
DATABASE = 'flaskr'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)

# get configuration details (either from this or external file)
app.config.from_object(__name__)

# Set this environment variable using export FLASKR_SETTINGS=....
#FLASKR_SETTINGS = '/Users/mike/SkyDrive/Personal/Education/flask/flaskr/FLASKR_SETTINGS.ini'
#app.config.from_envvar('FLASKR_SETTINGS', silent=False)

# Make sure you are installed
def connect_db():
	"""Returns a new connection to the Cloudant database."""
	app.logger.debug('Connecting to Cloudant database...')
	account = cloudant.Account(app.config['ACCOUNT'])
	return account.database(app.config['DATABASE'])
	#app.logger.debug('Connected to Cloudant database...')

def init_db():
	"""Creates the database views."""
	# This is not applicable when using _all_docs API
	db = connect_db()
	loader = couchdbkit.loaders.FileSystemDocsLoader('_design')
	loader.sync(db, verbose=True)

@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db()
    #Entry.set_db(g.db)

@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    # nothing here

@app.route('/')
def show_entries():
    # Using _all_docs API endpoint and setting include_docs=true
	options = dict(include_docs=True)
	entries = []
	for row in g.db.all_docs(params=options):
		print row
		doc = row['doc']
		if doc.get('text') and doc.get('title'):
			entries.append(doc)
	return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	app.logger.debug('before entry added')
	entry = dict(author='test', title=request.form['title'], text=request.form['text'], date=time.time())
	# Cloudant.py post() will convert to json and pass in body of http request to load document
	g.db.post(params=entry)	
	app.logger.debug('after entry added')
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

app.debug = True
app.logger.setLevel(logging.DEBUG)
 
#logging.basicConfig(filename='example.log',level=logging.INFO)

if __name__ == '__main__':
	app.run()
