from flask import Flask  # most basic thing
from flask import render_template
from flask import url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)  # referencing this file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # set up database; 3 / is relative path, 4 is absolute
db = SQLAlchemy(app)  # pass in the app; init the database


# set up data model (so we grab data and make objects?)
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(30), nullable=False)
    lname = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), nullable=True)  # some client might not speak or speak the language so not always useful
    # some other properties?
    info = db.Column(db.String(500), nullable=False)  # free text

    # this runs every time a row is created - not using now, for reference
    def __repr__(self):  
        return "<Client {} created>".format(self.id)


# set up routing
# root (client view)
@app.route('/') # url string here
def index():  # function of that url
    return render_template('index.html')

# pages for carers views
@app.route('/carer-view/<name>-<start_of_shift>')
def client_view(name, start_of_shift):
    # TODO: make HTML page for it(them)
    # TODO a function to convert time formats from url input
    return f"Carer view for {name} at {start_of_shift}"

# page for notes/diary
@app.route('/notes')
def notes():
    # TODO: point to this page from the carer pages
    return "this is notes page"

# page for the questionnaire
@app.route('/questionnaire')
def questionnaire():
    # TODO: point to this page from the carer pages
    return "this is questions page"

# run the thing
if __name__ == "__main__":
    app.run(debug=True)  # enable debug mode
# go to localhost:5000 and you can see the app!