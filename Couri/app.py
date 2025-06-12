from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for session management

# Simple in-memory user store: {email: {first_name, last_name, password}}
users = {}

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        password = request.form.get('password', '')

        # Basic checks
        if '@' not in email or not email or not password:
            error = 'Incorrect email or password'
        else:
            user = users.get(email)
            if not user or user['password'] != password:
                error = 'Incorrect email or password'

        if error:
            return render_template('loginpage.html', error=error)

        # Login success
        session['user_email'] = email
        session['user_first_name'] = user['first_name']
        return redirect(url_for('welcome'))

    return render_template('loginpage.html', error=error)

@app.route('/create-account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')

        if not (first_name and last_name and email and password):
            return render_template('createaccount.html', error='Please fill out all fields')

        if email in users:
            return render_template('createaccount.html', error='An account with that email already exists.')

        # Save user
        users[email] = {
            'first_name': first_name,
            'last_name': last_name,
            'password': password
        }
        session['user_email'] = email
        session['user_first_name'] = first_name
        return redirect(url_for('welcome'))

    return render_template('createaccount.html')

@app.route('/welcome')
def welcome():
    if 'user_email' not in session:
        return redirect(url_for('homepage'))
    return render_template('welcome.html', first_name=session.get('user_first_name'))

@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('homepage'))

if __name__ == '__main__':
    app.run(debug=True)