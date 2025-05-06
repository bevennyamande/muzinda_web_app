import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'super_secure_random_secret'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# -----------------------------
# USER CLASS AND DATABASE SETUP
# -----------------------------

class UserNotFoundError(Exception):
    pass


class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.password = self.get_password(username)

    @staticmethod
    def get_password(username):
        with sqlite3.connect('database.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            return result[0] if result else None

    @classmethod
    def get(cls, username):
        password = cls.get_password(username)
        if password:
            return cls(username)
        return None


@login_manager.user_loader
def load_user(username):
    return User.get(username)


# -----------------------------
# DB INITIALIZATION (ONCE)
# -----------------------------

def init_db():
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users(
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT)
        ''')
        db.commit()

        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users VALUES (?, ?, ?)", ('admin', 'admin', 'admin@example.com'))
            db.commit()


# -----------------------------
# ROUTES
# -----------------------------

@app.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.get(request.form['username'])
        if user and request.form['password'] == user.password:
            login_user(user)
            session['username'] = user.id
            return redirect(url_for('home'))
        else:
            return redirect(url_for('invalid'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['password2']
        email = request.form['email']

        if password != confirm:
            return render_template('invalid.html', error="Passwords do not match.")

        try:
            with sqlite3.connect('database.db') as con:
                c = con.cursor()
                c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, password, email))
                con.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('invalid.html', error="Username already exists.")
    return render_template('register.html')


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/developers')
@login_required
def developers():
    return render_template('developers.html')


@app.route('/projects')
@login_required
def projects():
    return render_template('projects.html')


@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html', logged=current_user.is_authenticated)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/invalid')
def invalid():
    return render_template('invalid.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    return redirect(url_for('login'))


# -----------------------------
# ENTRY POINT
# -----------------------------

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

