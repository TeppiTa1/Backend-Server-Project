#import Flask library and SQLAlchemy that support Flask into the program
from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Create an instance of the Flask class
app = Flask(__name__)
app.secret_key = "Super_Secret_DoFe_Key"  # Needed for session management and flash messages

# --- DATABASE CONFIGURATION ---
# This is the code that tells SQLAlchemy where our database is.
# Format: mysql+pymysql://<username>:<password>@<host>/<database_name>
# For XAMPP default: username is 'root', there is no password, host is 'localhost', and the project's database 'dofe_project'
# app.config[] can be understand as a dictionary that hold all the configuration setting for Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/dofe_project'
# URI stand for Uniform Resource Identifier - essentially the "address" of your database.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Disable unwanted feature of SQLAlchemy that isn't needed for this project
db = SQLAlchemy(app)
# Creates the actual instance of the SQLAlchemy translator and links it directly to the Flask app. This 'database' object is now your primary tool for all database operations.

bcrypt = Bcrypt(app)

# Create a python class named 'User'. This 'User' class will inherits from database.Model, which is a base class that is provided by Flask-SQLAlchemy
# Essentially give the User class all the database powes
# Model : A class that represent a database table
class User(db.Model):
    # __tablename__ specify the name of the database table that this class represents
    __tablename__ = 'users'
    # db.Column means this is a column in the database table
    # db.Integer means the data type of this column is Integer
    # primary_key = True means this column is the primary key of the table
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True, nullable = False)
    # unique = True means this column must have unique value for each row
    # nullable = False means this column cannot be empty
    # db.String(<number>) means the data type of this column is String with maximum length of <number> characters
    email = db.Column(db.String(120), unique = True, nullable = False)
    password_hash = db.Column(db.String(255), nullable = False)


    posts = db.relationship('Post', backref='author', lazy=True)

    # This is a special type of method that is used to represent(__repr__) the object as a string
    # It defines a string that will be printed if you ever try to print a User object. 
    def __repr__(self):
        # in this example, it will return the string '<User {username}>', where {username} is replaced with the actual username of the User object.
        return f'<User {self.username}>'
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False) # 'Text' is for long paragraphs
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Post {self.title}>'

# --- ROUTES ---
# define a route for the home page
@app.route('/')
def home():
    posts = Post.query.all() 
    users = User.query.all() # Get all users
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('home.html', posts=posts, user=user)
    else:
        return render_template('home.html', posts=posts, user=None)
    

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    # 1. SECURITY CHECK: Is the user logged in?
    if 'user_id' not in session:
        flash("You must be logged in to create a post.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        # 2. Get the current user's ID from the session
        current_user_id = session['user_id']

        # 3. Create the Post, assigning the Foreign Key (user_id)
        new_post = Post(title=title, content=content, user_id=current_user_id)
        
        db.session.add(new_post)
        db.session.commit()
        
        flash("Post created successfully!", "success")
        return redirect(url_for('home'))

    return render_template('create_post.html')

# A new route to test our database connection
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Query the database for a user with the provided username
        user = User.query.filter_by(username=username).first()

        # check_password_hash takes two arguments:
        # 1. The HASH stored in the database (user.password_hash)
        # 2. The PLAIN password the user just typed (password)
        # It handles the un-mashing and comparison securely behind the scenes
        if user and check_password_hash(user.password_hash, password):
            # Store user ID in session to keep the user logged in
            session['user_id'] = user.id
            flash("Logged in successfully!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Remove user ID from session to log the user out
    session.pop('user_id', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Basic password validation
        #if password is less than 8 characters, flash error message and redirect back to register page
        if len(password) < 8:
            flash("Password must be at least 8 characters long!", "error")
            return redirect(url_for('register'))
        #if password does not contain at least one number, flash error message and redirect back to register page
        if not any(char.isdigit() for char in password):
            flash("Password must contain at least one number!", "error")
            return redirect(url_for('register'))
        #if password does not contain at least one uppercase letter, flash error message and redirect back to register page
        if not any(char.isupper() for char in password):
            flash("Password must contain at least one uppercase letter!", "error")
            return redirect(url_for('register'))
        #if password does not contain at least one special character, flash error message and redirect back to register page
        special_characters = "!@#$%^&*()-+?_=,<>/"
        if not any(char in special_characters for char in password):
            flash("Password must contain at least one special character!", "error")
            return redirect(url_for('register'))
        

        # Check if the username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("User with that name already exist!", "error")
            return redirect(url_for('register'))
        
        # Create a new user instance
        #new_user = User(username=username, email=email, password_hash=password) <- Insecure way
        # Secure way: Hash the password before storing it
        hashed_password = generate_password_hash(password, method='scrypt')
        
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! You will now be redirected to login page...", "success")
        return redirect(url_for('login'))
    return render_template('register.html')




@app.route('/testdb')
def test_db_connection():
    try:
        # This is how you query the database with SQLAlchemy
        # Here we are trying to get the first user from the User table
        user = User.query.first()
        # If there is at least one user, display the username
        if user:
            return f'<h1>Success!</h1><p>The first user in the database is: {user.username}</p>'
        else:
            # If there are no users in the table, inform the user
            return '<h1>Success!</h1><p>The connection is working, but the user table is empty.</p>'
    except Exception as e:
        # If there is any error, display the error message
        return f'<h1>Error!</h1><p>There was an error connecting to the database: {e}</p>'

# --- UPDATE POST ROUTE ---    
@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
def update_post(post_id):
    # 1. Fetch the post from the DB by ID. 
    # If it doesn't exist, return a 404 error automatically.
    post = Post.query.get_or_404(post_id)

    # 2. CHECK AUTHORIZATION
    # Is the user logged in? AND Is the logged-in user the author?
    if 'user_id' not in session or post.author.id != session['user_id']:
        abort(403) # 403 means "Forbidden" - You don't have permission.
    
    if request.method == 'POST':
        # 3. Update the post data
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        
        # 4. Commit changes (No need to db.session.add() for updates)
        db.session.commit()
    
        flash('Your post has been updated!', 'success')
        return redirect(url_for('home'))

    return render_template('update_post.html', post=post)

# --- DELETE POST ROUTE ---
@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    # 1. CHECK AUTHORIZATION (Crucial!)
    if 'user_id' not in session or post.author.id != session['user_id']:
        abort(403)
    
    # 2. Delete the post
    db.session.delete(post)
    db.session.commit()
    
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

# --- RUN THE APP ---
# like last time, this code check if it is being run directly (not imported as a module in another script)
if __name__ == '__main__':
    app.run(debug=True)


