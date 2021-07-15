from flask import Flask  # most basic thing
from flask import render_template
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime, timedelta, date, time


app = Flask(__name__)  # referencing this file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # set up database; 3 / is relative path, 4 is absolute
db = SQLAlchemy(app)  # pass in the app; init the database


# set up data model
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(30), nullable=False)
    lname = db.Column(db.String(30), nullable=False)
    dob = db.Column(db.DateTime, nullable=False) 
    address = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), nullable=True)  # some client might not speak or speak the language so not always useful
    # some other properties?
    info = db.Column(db.String(500), nullable=False)  # free text

    # this runs every time a row is created - not using now, for reference
    def __repr__(self):  
        return "<Client {} created>".format(self.id)

class ClientInterest(db.Model):
    client_id = db.Column(db.Integer, primary_key=True) 
    interest_num = db.Column(db.Integer, primary_key=True)  # is this how to do compound pk in Flask??
    interest_text = db.Column(db.String(100), nullable=False)

    def __repr__(self):  
        return "<Client Interest {} created>".format(self.id)

class ClientGoal(db.Model):
    client_id = db.Column(db.Integer, primary_key=True)
    goal_num = db.Column(db.Integer, primary_key=True)
    goal_text = db.Column(db.String(100), nullable=False)
        
    def __repr__(self):  
        return "<Client Goal {} created>".format(self.id)

# the "lookup table" for all needs
class SpecialNeed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sn_name = db.Column(db.String(30), nullable=False)

    def __repr__(self):  
        return "<Special Need {} created>".format(self.id)

# linking table for needs
class ClientSpecialNeed(db.Model):
    client_id = db.Column(db.Integer, primary_key=True)
    sn_id = db.Column(db.Integer, primary_key=True)
    
    def __repr__(self):  
        return "<Client Special Need {} created>".format(self.id)

class Carer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(30), nullable=False)
    lname = db.Column(db.String(30),nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    
    def __repr__(self):  
        return "<Carer {} created>".format(self.id)

class Roster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carer_id = db.Column(db.Integer, nullable=False)
    client_id = db.Column(db.Integer, nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    finish = db.Column(db.DateTime, nullable=False)    

    def __repr__(self):  
        return "<Roster {} created>".format(self.id)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roster_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    essential = db.Column(db.Boolean, nullable=False)
    completed = db.Column(db.Boolean, nullable=False)

    def __repr__(self):  
        return "<Task {} created>".format(self.id)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    primary = db.Column(db.Boolean, nullable=False)    

    def __repr__(self):  
        return "<Contact {} created>".format(self.id)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, nullable=False)
    when = db.Column(db.DateTime, nullable=False)
    who = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)    

    def __repr__(self):  
        return "<Appointment {} created>".format(self.id)

class Communication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, nullable=False)
    carer_id = db.Column(db.Integer, nullable=False)
    when = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.String(500), nullable=False)

    def __repr__(self):  
        return "<Communication {} created>".format(self.id)


# helper functions
def str_to_bool(string):
    return string.lower() in ['y', 'yes', 't', 'true', '1']

def str_to_date_time(string):
    return datetime.strptime(string, "%d/%m/%Y %H:%M")

def str_to_date(string):
    return datetime.strptime(string, "%d/%m/%Y")


# set up routing
# root (client view)
@app.route('/') # url string here
def index():  # function of that url
    return render_template('index.html')

# page for client brief page (after log in)
@app.route('/client-brief/<fname>-<lname>-<start_of_shift>')
def client_view(fname, lname, start_of_shift):
    # TODO a function to convert time formats from url input
    return render_template('client_brief.html', fname=fname, lname=lname, start_of_shift=start_of_shift)

# page for shift info (after shift start)
@app.route('/shift-view/<fname>-<lname>-<start_of_shift>', methods=['GET', 'POST'])
def shift_view(fname, lname, start_of_shift):
    # get client, carer and roster object for later 
    current_client = Client.query.filter_by(id='1').first()  # TODO hardcoded - fine for demoing purpose
    current_carer = Carer.query.filter_by(fname=fname, lname=lname).first()
    start_time = datetime.combine(datetime.today(), datetime.strptime(start_of_shift, "%H%M").time())
    current_roster = Roster.query.filter_by(client_id=current_client, 
                                            carer_id=current_carer, 
                                            start=start_time)
    
    # TODO get task list (this shift & all)
    tasks = Task.query.filter()
    all_tasks = Task.query.filter()

    # get today's time range
    today_start = datetime.combine(date.today(), time())
    today_end = datetime.combine(date.today()+timedelta(days=1), time())

    # TODO get appointments
    appointments = Appointment.query.filter_by(when.between,
                                            client_id=current_client).all()
    
    # get the list of notes TODO
    communications = Communication.query.filter_by(when.between(today_start, today_end),
                                                   client_id=current_client, 
                                                   carer_id=current_carer).all()
    
    # return f"Shift view for {fname} {lname} at {start_of_shift}"  # TODO: make HTML page for it(them)
    return render_template('client_shift.html', fname=fname, lname=lname, start_of_shift=start_of_shift)

# page for adding new note entry
@app.route('/shift-view/<fname>-<lname>-<start_of_shift>/add_note', methods=['POST'])
def add_note(fname, lname, start_of_shift):
    if request.method == 'POST':
        client = request.form['client_name']
        carer = request.form['carer_name']
        shift_start_time = request.form['shift']
        note_entry_time = request.form['datetime']
        note = request.form['note_content']

        new_note_entry = Communication()
        try:
            db.session.add(new_note_entry)
            db.session.commit()
            return redirect('/shift-view/<fname>-<lname>-<start_of_shift>')
        except:
            return 'There was an error creating this note entry'
    else:
        # get current time
        current_time = datetime.now().strftime("%H:%M:%S")
        current_datetime = datetime.today().strftime(("\%d-%m-%Y")) + current_time

        return render_template('add_note.html', fname=fname, lname=lname, 
            start_of_shift=start_of_shift, current_datetime = current_datetime)

# page for the questionnaire
@app.route('/questionnaire')
def questionnaire():
    # TODO: point to this page from the carer pages
    return "this is questions page"

# page for admin
@app.route('/admin', methods=['GET'])
def admin():
    clients = Client.query.order_by(Client.id).all()    
    client_interests = ClientInterest.query.order_by(ClientInterest.client_id).all()
    client_goals = ClientGoal.query.order_by(ClientGoal.client_id).all()
    special_needs = SpecialNeed.query.order_by(SpecialNeed.id).all()
    client_special_needs = ClientSpecialNeed.query.order_by(ClientSpecialNeed.sn_id).all()
    carers = Carer.query.order_by(Carer.id).all()
    rosters = Roster.query.order_by(Roster.id).all()
    tasks = Task.query.order_by(Task.id).all()
    appointments = Appointment.query.order_by(Appointment.id).all()
    contacts = Contact.query.order_by(Contact.id).all()
    communications = Communication.query.order_by(Communication.id).all()
    
    return render_template('admin.html', clients=clients, client_interests=client_interests, 
            client_goals=client_goals, special_needs=special_needs, client_special_needs=client_special_needs, 
            carers=carers, rosters=rosters, tasks=tasks, appointments=appointments, contacts=contacts, 
            communications=communications)

# admin - add table entity
@app.route('/admin/add-<table>', methods=['POST'])
def add(table):
    if table == 'client':
        fname = request.form['fname']
        lname = request.form['lname']
        address = request.form['address']
        dob = str_to_date(request.form['dob'])
        phone = request.form['phone']
        info = request.form['info']
    
        entity = Client(fname=fname, lname=lname, dob=dob, address=address, phone=phone, info=info)        
    
    elif table == 'client_interest':
        client_id = request.form['client_id']
        interest_num = request.form['interest_num']
        interest_text = request.form['interest_text']

        entity = ClientInterest(client_id=client_id, interest_num=interest_num, interest_text=interest_text)
    
    elif table == 'client_goal':
        client_id = request.form['client_id']
        goal_num = request.form['goal_num']
        goal_text = request.form['goal_text']

        entity = ClientGoal(client_id=client_id, goal_num=goal_num, goal_text=goal_text)
    
    elif table == 'special_need':        
        sn_name = request.form['sn_name']

        entity = SpecialNeed(sn_name=sn_name)
            
    elif table == 'client_special_need':
        client_id = request.form['client_id']
        sn_id = request.form['sn_id']

        entity = ClientSpecialNeed(client_id=client_id, sn_id=sn_id)

    elif table == 'carer':
        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form['phone']
    
        entity = Carer(fname=fname, lname=lname, phone=phone)

    elif table == 'roster':
        carer_id = request.form['carer_id']
        client_id = request.form['client_id']
        start = str_to_date_time(request.form['start'])
        finish = str_to_date_time(request.form['finish'])

        entity = Roster(carer_id=carer_id, client_id=client_id, start=start, finish=finish)

    elif table == 'task':
        roster_id = request.form['roster_id']
        description = request.form['description']
        essential = str_to_bool(request.form['essential'])
        completed = str_to_bool(request.form['completed'])
    
        entity = Task(roster_id=roster_id, description=description, essential=essential, completed=completed)

    elif table == 'appointment':
        client_id = request.form['client_id']
        when = str_to_date_time(request.form['when'])
        who = request.form['who']
        description = str_to_bool(request.form['description'])
        
        entity = Appointment(client_id=client_id, when=when, who=who, description=description)

    elif table == 'contact':
        client_id = request.form['client_id']
        name = request.form['name']
        phone = request.form['phone']
        primary = str_to_bool(request.form['primary'])    
    
        entity = Contact(client_id=client_id, name=name, phone=phone, primary=primary)

    elif table == 'communication':
        client_id = request.form['client_id']
        carer_id = request.form['carer_id']
        when = str_to_date_time(request.form['when'])
        message = request.form['message']
    
        entity = Communication(client_id=client_id, carer_id=carer_id, when=when, message=message)

    try:
        db.session.add(entity)
        db.session.commit()
        return redirect('/admin#' + table)
    except Exception as exception:
        return 'There was an issue adding the ' + table + '.<br>' + str(exception)

# delete
@app.route('/admin/delete-<table>/<int:id>')
def delete_single_id(table, id):
    return delete(table, id)

@app.route('/admin/delete-<table>/<int:id1>-<int:id2>')
def delete(table, id1, id2=None):
    if table == 'client':    
        entity = Client.query.get_or_404(id1)
    elif table == 'client_interest':
        entity = ClientInterest.query.filter_by(client_id=id1, interest_num=id2).first()
    elif table == 'client_goal':
        entity = ClientGoal.query.filter_by(client_id=id1, goal_num=id2).first()
    elif table == 'special_need':
        entity = SpecialNeed.query.get_or_404(id1)
    elif table == 'client_special_need':
        entity = ClientSpecialNeed.query.filter_by(client_id=id1, sn_id=id2).first()
    elif table == 'carer':
        entity = Carer.query.get_or_404(id1)
    elif table == 'roster':
        entity = Roster.query.get_or_404(id1)
    elif table == 'task':
        entity = Task.query.get_or_404(id1)
    elif table == 'appointment':
        entity = Appointment.query.get_or_404(id1)
    elif table == 'contact':
        entity = Contact.query.get_or_404(id1)
    elif table == 'communication':
        entity = Communication.query.get_or_404(id1)

    try:
        db.session.delete(entity)
        db.session.commit()
        return redirect('/admin#' + table)
    except Exception as exception:
        return 'There was a problem deleting the ' + table + '.<br>' + str(exception)


# create tables
@app.route('/admin/create_tables')
def create_tables():
    db.create_all()
    return redirect('/admin')

# create demo data
@app.route('/admin/create_demo_data')
def create_demo_data():        
    db.session.add(Client(id=101, fname='Celia', lname='Valentine', dob=datetime(1960,1,1), address='1 The Street, Melbourne 3000', info='A little bit of information about the client. What is their condition. What is their personality. How do the caregivers feel about her.'))
    db.session.commit()
    return redirect('/admin')

# run the thing
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)  # enable debug mode
# run "python app.py" in terminal then go to localhost:5000 and you can see the app!