# all the imports
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import datetime
from couchdbkit import Document, StringProperty, DateTimeProperty
import couchdbkit
import logging

# configuration (could also be in external file...see below)
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
# export FLASKR_SETTINGS = '/tmp/flaskr/FLASKR_SETTINGS.ini'
# app.config.from_envvar('FLASKR_SETTINGS', silent=False)

# Make sure couchdb and couchdbkit are installed
def connect_db():
	"""Returns a new connection to the database."""
	server = couchdbkit.Server()
	return server.get_or_create_db(app.config['DATABASE'])

def init_db():
	"""Creates the database views."""
	db = connect_db()
	loader = couchdbkit.loaders.FileSystemDocsLoader('_design')
	loader.sync(db, verbose=True)

class Entry(Document):
	author = StringProperty()
	date = DateTimeProperty()
	title = StringProperty()
	text = StringProperty()

@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db()
    Entry.set_db(g.db)

@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    # nothing here

@app.route('/')
def show_entries():
	# using a view (NOTE: you will have to create the appropriate view in CouchDB/Cloudant)
	# entries = g.db.view('entry/all', schema=Entry)
	# using the primary index _all_docs
	entries = g.db.all_docs(include_docs=True, schema=Entry)
	app.logger.debug(entries.all())
	return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	app.logger.debug('before entry added')
	entry = Entry(author='test', title=request.form['title'], text=request.form['text'], date=datetime.datetime.utcnow())
	g.db.save_doc(entry)	
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
app.logger.setLevel(logging.INFO)
 
# logging.basicConfig(filename='example.log',level=logging.INFO)
couchdbkit.set_logging('info')

if __name__ == '__main__':
	app.run()
