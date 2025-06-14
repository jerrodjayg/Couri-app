from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'Couri'  # Needed for session management

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        password = request.form.get('password', '')

        # Basic validation
        if '@' not in email or not email or not password:
            error = 'Incorrect email or password'
        else:
            user = User.query.filter_by(email=email).first()
            if not user or user.password != password:
                error = 'Incorrect email or password'

        if error:
            return render_template('loginpage.html', error=error)

        # Login success: save to session
        session['user_email'] = user.email
        session['user_first_name'] = user.first_name
        return redirect(url_for('welcome'))

    return render_template('loginpage.html', error=error)

@app.route('/create-account', methods=['GET', 'POST'])
def create_account():
    error = None
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')

        # Check if any field is empty
        if not (first_name and last_name and email and password):
            error = 'Please fill out all fields.'
            return render_template('createaccount.html', error=error)

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            error = 'An account with that email already exists.'
            return render_template('createaccount.html', error=error)

        # Create and save new user
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password  # NOTE: Use hashing in production
        )
        db.session.add(new_user)
        db.session.commit()

        # Log in the user
        session['user_email'] = new_user.email
        session['user_first_name'] = new_user.first_name
        return redirect(url_for('welcome'))

    return render_template('createaccount.html')

@app.route('/Welcome')
def welcome():
    if 'user_email' not in session:
        return redirect(url_for('homepage'))
    return render_template('welcome.html', first_name=session.get('user_first_name'))

@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('homepage'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
