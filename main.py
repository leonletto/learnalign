from flask import Flask, request, jsonify, flash, redirect, session, render_template
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
import os
import json
from routes import setup_routes

# auth = HTTPBasicAuth()

# setup the SQLAlchemy with the flask app
app = Flask(__name__)
app.secret_key = '8238f8hwefrw83eed'

# Load the database URL from the environment variable
dburl = os.getenv('DATABASE_URL')
if not dburl:
  dburl = 'postgresql://lettol@localhost:5432/lettol'
else:
  # change postgres to postgresql in the dburl
  dburl = dburl.replace('postgres', 'postgresql')

app.config['SQLALCHEMY_DATABASE_URI'] = dburl
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)
  role = db.Column(db.String(80), nullable=False)
  parent = db.Column(db.String(80))
  state = db.Column(db.Text)  # For storing the state as a JSON string


class Topic(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False)
  parent_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
  parent = db.relationship('Topic', remote_side=[id])
  notes = db.Column(db.Text)  # For storing the notes as a JSON string

def verify_password(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.password == password:
    return username


# After your User model
class CaInterface:

  def __init__(self, auth, User, db, Topic):
    self.auth = auth
    self.User = User
    self.db = db
    self.Topic = Topic
    self.base_path = '/ejbca/ejbca-rest-api/v1'
    self.interface_path = '/ejbca'

    self.app = setup_routes(app, auth, self.User, self.db, self.Topic,
                            self.interface_path, self.base_path)

    @app.route(f'{self.interface_path}/login', methods=['GET', 'POST'])
    def login():
      if request.method == 'POST':
        username = request.form.get('username').lower()
        password = request.form.get('password')
        if username and password and verify_password(username, password):
          session['logged_in'] = True
          session['username'] = username
          return redirect(f'{self.interface_path}/learner_setup', code=302)
        else:
          flash('Invalid username or password')
      return render_template('login.html')

    @app.route(f'{self.interface_path}/register', methods=['GET', 'POST'])
    def register():
      if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        username = request.form.get('username').lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        grade = request.form.get('grade', None)
        user_type = session.get('role')

        # First, check if the passwords match
        if password != confirm_password:
          flash('Passwords do not match.', 'danger')
          return redirect(f'{self.interface_path}/register', code=302)

        # Prepare the state as a JSON string
        statedict = {
          'firstname': firstname,
          'lastname': lastname,
          'email': email
        }
        if grade:
          statedict['grade'] = grade

        state = json.dumps(statedict)

        # Then, check if the username already exists in your database
        if self.user_exists(username):
          flash('Username already exists')
          return render_template('register.html')

        # If the passwords match and the username is not taken, create the user
        self.create_user(username, password, user_type, state)
        flash('Successfully registered')

        # Log the user in
        session['logged_in'] = True
        session['username'] = username

        # Redirect to the learner_setup route
        return redirect(f'{self.interface_path}/learner_setup', code=302)
      role = session.get('role')
      return render_template('register.html', role=role)

    @app.route(f'{self.interface_path}/persona_selection', methods=['GET', 'POST'])
    def persona_selection():
      if request.method == 'POST':
        session['role'] = request.form.get('persona')
        return redirect(f'{self.interface_path}/register', code=302)
      return render_template('persona_selection.html')

  def run(self):
    self.app.run(host='0.0.0.0', debug=True, port=81)

  def user_exists(self, username):
    user = User.query.filter_by(username=username).first()
    return user is not None

  def create_user(self, username, password, user_type, state):
    highest_id_user = User.query.order_by(User.id.desc()).first()
    new_id = (highest_id_user.id + 1) if highest_id_user else 1

    user = User(id=new_id, username=username, password=password, role=user_type, state=state)
    db.session.add(user)
    db.session.commit()


def main():
  auth = HTTPBasicAuth()

  ca_interface = CaInterface(auth, User, db, Topic)
  ca_interface.run()


if __name__ == '__main__':
  main()
