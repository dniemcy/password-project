from flask import Flask, render_template, request, jsonify, redirect, session, url_for, make_response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
import random

app = Flask(__name__)

app.secret_key = 'your secret key' # my stored key goes here

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Winter2009' # my root password goes here
app.config['MYSQL_DB'] = 'pythonlogin'


mysql = MySQL(app)

# Initial 
@app.route('/')
def index():
    return render_template('index.html')

# To login page
@app.route('/tologin')
def tologin():
    if 'remember' in request.cookies:
        username = request.cookies.get('remember')
        if username:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('home'))
    return render_template('login.html')

# Login action
@app.route('/login/', methods=['POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']

            if 'remember' in request.form:
                resp = make_response(redirect(url_for('home')))
                resp.set_cookie('remember', username, max_age=3600 * 24 * 30, path='/')  # 30 day expiration
                return resp

            return redirect(url_for('home'))
        
        else:
            msg = 'Incorrect username/password!'

    return render_template('login.html', msg=msg)

# Logout action (fron home page)
@app.route('/login/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   resp = redirect(url_for('tologin'))
   resp.delete_cookie('remember')
   return resp

# Registration action
@app.route('/login/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

# To registration page
@app.route('/toregister')
def toregister():
    return render_template('register.html')

# Home page
@app.route('/login/home')
def home():
    if 'loggedin' in session:
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.execute('SELECT * FROM passwords WHERE user_id = %s', (user_id,))
        passwords = cursor.fetchall()
        cursor.close()
        return render_template('home.html', username=user['username'], email=user['email'], passwords=passwords)
    return redirect(url_for('login'))

# Profile page with user information
@app.route('/login/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

# New passwords on home page
@app.route('/save-password', methods=['POST'])
def save_password():
    if 'loggedin' in session:
        user_id = session['id']
        website_name = request.form['website']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO passwords (user_id, website_name, password) VALUES (%s, %s, %s)', (user_id, website_name, password))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('home'))
    return redirect(url_for('login'))

# Password Generator Below ----------------------

# Full character strings
lowercase_characters = 'abcdefghijklmnopqrstuvwxyz'
uppercase_characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
numbers = '0123456789'
symbols = '!@#$%^&*()[]{}/-_+=~`<>;:,.?|'

@app.route('/generate-password', methods=['POST'])
def generate_password():
    lowercase = request.form.get('lowercase', 'n')
    uppercase = request.form.get('uppercase', 'n')
    numbers_incl = request.form.get('numbers', 'n')
    symbols_incl = request.form.get('symbols', 'n')
    length = int(request.form.get('length', 0))

    characters = character_selector(lowercase, uppercase, numbers_incl, symbols_incl)

    if not characters:  # Check if no characters are selected
        return jsonify({'error': 'Please select at least one character set.'})
    
    random_password = print_random_password(length, characters)
    return jsonify({'password': random_password})

def character_selector(lowercase, uppercase, numbers_incl, symbols_incl):
    all_characters = ''
    if lowercase == "y":
        all_characters += lowercase_characters
    if uppercase == "y":
        all_characters += uppercase_characters
    if numbers_incl == "y":
        all_characters += numbers
    if symbols_incl == "y":
        all_characters += symbols
    return all_characters

def print_random_password(length, characters):
    password = ''
    for _ in range(length):
        password += random.choice(characters)
    return password

if __name__ == '__main__':
    app.run(debug=True)