from flask import Flask, request, flash, redirect, session, render_template
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
import time
import json

from sqlalchemy import text
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

from routes import setup_routes
from sqlalchemy.exc import OperationalError
from flask_apscheduler import APScheduler


def keep_db_awake():
  with app.app_context():
    try:
      db.session.execute(text("SELECT 1"))
    except OperationalError:
      print("Error while executing keep-alive query.")
    else:
      print("Keep-alive query executed successfully.")


class Config(object):
  TZ = 'America/Los_Angeles'
  JOBS = [{
    'id': 'keep_db_awake',
    'func': '__main__:keep_db_awake',
    'trigger': 'interval',
    'minutes': 4,
  }]

  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'  # Updated for SQLite
  SECRET_KEY = '8238f8hwefrw83eed'
  SCHEDULER_API_ENABLED = True


# setup the SQLAlchemy with the flask app
app = Flask(__name__)
app.config.from_object(Config())

db = SQLAlchemy(app)


# enforce foreign key constraints in SQLite
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
  if isinstance(dbapi_connection, SQLite3Connection):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

####


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
          print(f'Logged in as {username}'.format(username))
          print(session)
          return redirect(f'{self.interface_path}/learning_tracks', code=302)
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
          return render_template('register.html', role=user_type)

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
          return render_template('register.html', role=user_type)

        # If the passwords match and the username is not taken, create the user
        self.create_user(username, password, user_type, state)
        flash('Successfully registered')

        # Log the user in
        session['logged_in'] = True
        session['username'] = username

        # Redirect to the learner_setup route
        if session['role'] == 'guardian':
          return redirect(f'{self.interface_path}/parent', code=302)
        else:
          return redirect(f'{self.interface_path}/learner_setup', code=302)

      print(session['role'])
      role = session['role']
      return render_template('register.html', role=role)

    @app.route(f'{self.interface_path}/persona_selection',
               methods=['GET', 'POST'])
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
    # check if the user exists in the database
    check_user = User.query.filter_by(username=username).first()
    if check_user:
      return False

    user = User(id=new_id,
                username=username,
                password=password,
                role=user_type,
                state=state)
    db.session.add(user)
    db.session.commit()


def main():
  auth = HTTPBasicAuth()

  ca_interface = CaInterface(auth, User, db, Topic)

  with app.app_context():
    db.create_all()
    # Try to connect to the database
    for _ in range(3):  # Retry 3 times
      try:
        db.session.execute(
          text("SELECT 1"))  # Simple query to check if DB connection works
        break
      except OperationalError:  # If connection does not work, wait and retry
        print("Database not ready, waiting...")
        time.sleep(5)  # Wait for 5 seconds before retrying
    else:
      print("Could not connect to the database.")
      return render_template(
        '503.html'
      ), 503  # Return a 503 error if the DB is not ready after 3 attempts

  # If the database is ready, run the app

  ca_interface.run()


if __name__ == '__main__':
  main()
