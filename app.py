import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user, session

app = Flask(__name__)
app.secret_key = 'ag;lagakjfkgjjjjjjjjl;hgfhjjjjjjjj'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'


class UserNotFoundError(Exception):
    pass


class User(UserMixin):
    '''User class for logging in '''
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute('''
    	CREATE TABLE IF NOT EXISTS users(username TEXT NOT NULL UNIQUE,
    		password TEXT NOT NULL,
			email TEXT)
		''')
    db.commit()
    cursor.execute('''SELECT username, password FROM users''')
    rows = cursor.fetchall()
    # username: password
    USERS = {username : password for username, password in rows}


    def __init__(self, id):
        if not id in self.USERS.keys():
            raise UserNotFoundError()
        self.id = id
        self.password = self.USERS[id]

    @classmethod
    def get(self_class, id):
        '''Return user instance of id, return None if not exist'''
        try:
            return self_class(id)
        except UserNotFoundError:
            return None


@login_manager.user_loader
def load_user(id):
    return User.get(id)


@app.before_request
def connect_db():
	try:
		db = sqlite3.connect('database.db')
		cursor = db.cursor()
		cursor.execute('''INSERT INTO users VALUES('admin','admin',
			'bevennyamande@gmail.com')''')
		db.commit()
	except sqlite3.DatabaseError as e:
		#logging.error(e)
		print(e)


@app.after_request
def after_request(response):
	'''Close the database connection after each request.'''
	db = sqlite3.connect('database.db')
	db.close()
	return response


@app.route('/',methods=['GET','POST'])
def index():
	if 'username' in session and request.method == 'GET':
		return render_template('home.html')
	elif request.method == 'GET':
		# the default home page
		return render_template('index.html')
	else:
		pass


@app.route('/login',methods=['GET','POST'])
def login():
	# check validation of input
	# if the user is the correct set cookie
	# database of user
	if request.method == 'POST':
		user = User.get(request.form['username'])
		if user and request.form['password'] == user.password:
			session['username'] = login_user(user)
			return redirect(url_for('home'))
		else:
			return redirect(url_for('invalid'))
	else:
		return render_template('login.html')


@app.route('/invalid')
def invalid():
	return render_template('invalid.html')


@app.route('/home')
@login_required
def home():
	# login required
	if not 'username' in session:
		return render_template('invalid.html')
	return render_template('home.html')


@app.route('/developers')
@login_required
def developers():
	# login required
	return render_template('developers.html')


@app.route('/projects')
@login_required
def projects():
	# login required
	return render_template('projects.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
	# validation of the new user
	# implement email validation
	# clicks link from email and get authorized
	if request.method == 'GET':
		return render_template('register.html')
	else:
		# remember to add to database
		data = request.form['username'],request.form['password']
		if data[1] == request.form['password2']:
			try:
				data = (request.form['username'],
					request.form['password'],
					request.form['email'])
				con = sqlite3.connect('database.db')
				c = con.cursor()
				c.execute('''INSERT INTO users VALUES(?,?,?)''', (data))
				con.commit()
				con.close()
			except sqlite3.DatabaseError as e:
				return render_template('invalid.html', error=e)
		else:
			# popout box for un matching passwords
			mismatch = 'passwords dont match'
			return render_template('invalid.html', error=mismatch)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
	# display the contact information
	# remember to hide some navbar titles
	if request.method == 'GET':
		if 'username' in session:
			logged = True
			# remember to include javascript for unauthenticated users
			return render_template('contact.html', logged=logged)
		else:
			return render_template('contact.html')
	else:
		pass


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def logout():
	logout_user()
	session.pop('username')
	return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
