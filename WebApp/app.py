from flask import Flask  # most basic thing
from flask import render_template
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime


app = Flask(__name__)  # referencing this file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # set up database; 3 / is relative path, 4 is absolute
db = SQLAlchemy(app)  # pass in the app; init the database


# set up data model 
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

class Roster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carer_id = db.Column(db.Integer, nullable=False)
    client_id = db.Column(db.Integer, nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    finish = db.Column(db.DateTime, nullable=False)    

    # this runs every time a row is created - not using now, for reference
    def __repr__(self):  
        return "<Roster {} created>".format(self.id)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roster_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    essential = db.Column(db.Boolean, nullable=False)
    completed = db.Column(db.Boolean, nullable=False)

    # this runs every time a row is created - not using now, for reference
    def __repr__(self):  
        return "<Task {} created>".format(self.id)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    primary = db.Column(db.Boolean, nullable=False)    

    # this runs every time a row is created - not using now, for reference
    def __repr__(self):  
        return "<Contact {} created>".format(self.id)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, nullable=False)
    when = db.Column(db.DateTime, nullable=False)
    who = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)    

    # this runs every time a row is created - not using now, for reference
    def __repr__(self):  
        return "<Appointment {} created>".format(self.id)

class Communication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, nullable=False)
    carer_id = db.Column(db.Integer, nullable=False)
    when = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.String(500), nullable=False)

    # this runs every time a row is created - not using now, for reference
    def __repr__(self):  
        return "<Communication {} created>".format(self.id)


# set up routing
# root (client view)
@app.route('/') # url string here
def index():  # function of that url
    return render_template('index.html')

# pages for carers views
@app.route('/carer-view/<fname>-<lname>-<start_of_shift>')
def client_view(fname, lname, start_of_shift):
    # TODO a function to convert time formats from url input
    # return f"Carer view for {fname} {lname} at {start_of_shift}"  # TODO: make HTML page for it(them)
    return render_template('carer.html', fname=fname, lname=lname, start_of_shift=start_of_shift)

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

# page for admin
@app.route('/admin', methods=['GET'])
def admin():
    clients = Client.query.order_by(Client.id).all()
    rosters = Roster.query.order_by(Roster.id).all()
    tasks = Task.query.order_by(Task.id).all()
    appointments = Appointment.query.order_by(Appointment.id).all()
    contacts = Contact.query.order_by(Contact.id).all()
    communications = Communication.query.order_by(Communication.id).all()
    
    return render_template('admin.html', clients=clients, rosters=rosters, tasks=tasks, appointments=appointments, contacts=contacts, communications=communications)

# admin - add client
@app.route('/admin/add-client', methods=['POST'])
def add_client():
    fname = request.form['fname']
    lname = request.form['lname']
    address = request.form['address']
    phone = request.form['phone']
    info = request.form['info']
    
    client = Client(fname=fname, lname=lname, address=address, phone=phone, info=info)

    try:
        db.session.add(client)
        db.session.commit()
        return redirect('/admin#client')
    except Exception as exception:
        return 'There was an issue adding the client.<br>' + str(exception)

# admin - add roster
@app.route('/admin/add-roster', methods=['POST'])
def add_roster():
    carer_id = request.form['carer_id']
    client_id = request.form['client_id']
    start = str_to_date_time(request.form['start'])
    finish = str_to_date_time(request.form['finish'])

    roster = Roster(carer_id=carer_id, client_id=client_id, start=start, finish=finish)

    try:
        db.session.add(roster)
        db.session.commit()
        return redirect('/admin#roster')
    except Exception as exception:
        return 'There was an issue adding the roster.<br>' + str(exception)

# admin - add task
@app.route('/admin/add-task', methods=['POST'])
def add_task():
    roster_id = request.form['roster_id']
    description = request.form['description']
    essential = str_to_bool(request.form['essential'])
    completed = str_to_bool(request.form['completed'])
    
    task = Task(roster_id=roster_id, description=description, essential=essential, completed=completed)

    try:
        db.session.add(task)
        db.session.commit()
        return redirect('/admin#task')
    except Exception as exception:
        return 'There was an issue adding the task.<br>' + str(exception)

# admin - add appointment
@app.route('/admin/add-appointment', methods=['POST'])
def add_appointment():
    client_id = request.form['client_id']
    when = str_to_date_time(request.form['when'])
    who = request.form['who']
    description = str_to_bool(request.form['description'])
    
    appointment = Appointment(client_id=client_id, when=when, who=who, description=description)

    try:
        db.session.add(appointment)
        db.session.commit()
        return redirect('/admin#appointment')
    except Exception as exception:
        return 'There was an issue adding the appointment.<br>' + str(exception)

# admin - add contact
@app.route('/admin/add-contact', methods=['POST'])
def add_contact():
    client_id = request.form['client_id']
    name = request.form['name']
    phone = request.form['phone']
    primary = str_to_bool(request.form['primary'])    
    
    contact = Contact(client_id=client_id, name=name, phone=phone, primary=primary)

    try:
        db.session.add(contact)
        db.session.commit()
        return redirect('/admin#contact')
    except Exception as exception:        
        return 'There was an issue adding the contact.<br>' + str(exception)

# admin - add communication
@app.route('/admin/add-communication', methods=['POST'])
def add_communication():
    client_id = request.form['client_id']
    carer_id = request.form['carer_id']
    when = str_to_date_time(request.form['when'])
    message = request.form['message']
    
    communication = Communication(client_id=client_id, carer_id=carer_id, when=when, message=message)

    try:
        db.session.add(communication)
        db.session.commit()
        return redirect('/admin#communication')
    except Exception as exception:
        return 'There was an issue adding the communication.<br>' + str(exception)

# delete
@app.route('/admin/delete-<table>/<int:id>')
def delete(table, id):
    if table == 'client':    
        entity = Client.query.get_or_404(id)
    elif table == 'roster':
        entity = Roster.query.get_or_404(id)
    elif table == 'task':
        entity = Task.query.get_or_404(id)
    elif table == 'appointment':
        entity = Appointment.query.get_or_404(id)
    elif table == 'contact':
        entity = Contact.query.get_or_404(id)
    elif table == 'communication':
        entity = Communication.query.get_or_404(id)

    try:
        db.session.delete(entity)
        db.session.commit()
        return redirect('/admin')
    except Exception as exception:
        return 'There was a problem deleting the ' + table + '.<br>' + str(exception)

def str_to_bool(string):
    return string.lower() in ['y', 'yes', 't', 'true', '1']

def str_to_date_time(string):
    return datetime.strptime(string, "%d/%m/%Y %H:%M")

# create tables
@app.route('/admin/create_tables')
def create_tables():
    db.create_all()
    return redirect('/admin')


# run the thing
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)  # enable debug mode
# run "python app.py" in terminal then go to localhost:5000 and you can see the app!