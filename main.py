#import Flask library into the program
from flask import Flask

# 2. Create an instance of the Flask class
# This is an essential concept in programming called: Object - Oriented Programming
# Class is basically a blueprint within the library of 'Flask' that defines things that a web server needs to know 
# (ie. handle web request, understand URL etc.)
# Instance is the actual stuff that I going to build
app = Flask(__name__)
# Double underscore name (__name__) is just a special module in python, allowing Flask know where to look for templete file

# 3. Define a "route" for the homepage
# The @app.route('/') decorator tells Flask: 
# "When someone visits the main homepage ('/'), run the function below."
@app.route("/")
# @ signifies its a Decorator
def home():
    # 4. The function that runs for this route
    # Because its in a function, it need to return something to display it in the browser
    return True

# 5. A standard Python block that ensures this code only runs
# when you execute the script directly (not when it's imported by another script)
if __name__ == "__main__":
    # 6. Start the Flask development server
    # debug=True allow the server to auto-reload when a save changes
    # it also provide better error messages
    app.run(debug = True)