#import Flask library and SQLAlchemy that support Flask into the program
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create an instance of the Flask class
app = Flask(__name__)

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
    password_hash = db.Column(db.String(120), nullable = False)

    # This is a special type of method that is used to represent(__repr__) the object as a string
    # It defines a string that will be printed if you ever try to print a User object. 
    def __repr__(self):
        # in this example, it will return the string '<User {username}>', where {username} is replaced with the actual username of the User object.
        return f'<User {self.username}>'
    
# --- ROUTES ---
# define a route for the home page
@app.route('/')
def home():
    return "Hello, DOFE Project!"

# A new route to test our database connection
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
    
# --- RUN THE APP ---
# like last time, this code check if it is being run directly (not imported as a module in another script)
if __name__ == '__main__':
    app.run(debug=True)


