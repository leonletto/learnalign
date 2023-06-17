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


# @app.before_first_request
# def create_tables():
#   if not User.__table__.exists(bind=db.engine):
#     db.create_all()
#
#     users = {
#       "admin": {
#         "password": "learnalign",
#         "role": "admin"
#       },
#       "cathy": {
#         "password": "password",
#         "role": "parent"
#       },
#       "joey": {
#         "password": "password",
#         "role": "student",
#         "parent": "cathy"
#       },
#       "mike": {
#         "password": "password",
#         "role": "student"
#       },
#       "mary": {
#         "password": "password",
#         "role": "content"
#       },
#     }
#
#     for username, data in users.items():
#       user = User.query.filter_by(username=username).first()
#       if not user:
#         new_user = User(username=username,
#                         password=data["password"],
#                         role=data["role"])
#         if "parent" in data:
#           new_user.parent = data["parent"]
#         db.session.add(new_user)
#
#     db.session.commit()


def populate_db(data, parent=None):
  for topic_name, subtopics in data.items():
    # Create a new topic
    topic = Topic(name=topic_name, parent=parent)
    db.session.add(topic)

    # If this topic has notes, convert them to a JSON string and store them
    notes = subtopics.get('Notes')
    if notes:
      topic.notes = json.dumps(notes)

    # Commit changes to save the new topic
    db.session.commit()

    # If there are subtopics, recursively add them to the database
    if subtopics and not notes:  # Avoid recursion if 'Notes' key is present
      populate_db(subtopics, topic)


json_data = {
  "Social Studies": {
    "US History I": {},
    "Survey of World History": {},
    "US History II": {},
    "US Government": {}
  },
  "Science": {
    "Biology": {},
    "Chemistry": {},
    "Physics": {}
  },
  "Language Arts": {
    "Mechanics of writing": {},
    "Literature analysis and citing sources": {},
    "Reading comprehension and writing reports": {}
  },
  "Electives": {
    "Environmental Science": {},
    "Sociology": {},
    "Intro to Communications and Speech": {},
    "Art History I": {},
    "Psychology": {},
    "Concepts in Probability and Statistics": {},
    "Intro to Art": {},
    "Contemporary Health": {},
    "Foundations of Personal Wellness": {},
    "Lifetime Fitness": {},
    "Strategies for Academic Success": {},
    "Healthy Living": {},
    "Economics": {},
    "Personal Finance": {}
  },
  "Math": {
    "Representing Relationships": {
      "Notes": [
        "Quantitative Reasoning", "Dimensional Analysis",
        "Writing and Solving Equations in Two Variables",
        "Writing and Graphing Equations in Two Variables",
        "Introduction to Functions", "Function Notation",
        "Evaluating Functions", "Analyzing Graphs", "Analyzing Tables",
        "Recognizing Patterns"
      ]
    },
    "Linear Functions": {
      "Notes": [
        "Introduction to Linear Functions", "Slope of a Line",
        "Slope-Intercept Form of a Line", "Point-Slope Form of a Line",
        "Writing Linear Equations", "Special Linear Relations"
      ]
    },
    "Linear Equations and Inequalities": {
      "Notes": [
        "Solving Linear Equations: Variable on One Side",
        "Solving Linear Equations: Variables on Both Sides",
        "Solving Linear Equations: Distributive Property",
        "Solving Mixture Problems", "Solving Rate Problems",
        "Literal Equations", "Solving Absolute Value Equations",
        "Solving One-Variable Inequalities",
        "Introduction to Compound Inequalities"
      ]
    },
    "Systems of Equations and Inequalities": {
      "Notes": [
        "Solving Systems of Linear Equations: Graphing",
        "Solving Systems of Linear Equations: Substitution",
        "Solving Systems: Introduction to Linear Combinations",
        "Solving Systems of Linear Equations: Linear Combinations",
        "Modeling with Systems of Linear Equations",
        "Graphing Two-Variable Linear Inequalities",
        "Modeling with Two-Variable Linear Inequalities",
        "Solving Systems of Linear Inequalities",
        "Modeling with Systems of Linear Inequalities"
      ]
    },
    "Nonlinear Functions": {
      "Notes": [
        "Linear Piecewise Defined Functions", "Step Functions",
        "Absolute Value Functions and Translations",
        "Reflections and Dilations of Absolute Value Functions",
        "The Square Root Function", "The Cube Root Function",
        "Performance Task: Construct and Analyze Piecewise Functions",
        "Cumulative Exam"
      ]
    },
    "Exponential Functions": {
      "Notes": [
        "Exponential Growth Functions", "Exponential Decay Functions",
        "Vertical Stretches and Shrinks of Exponential Functions",
        "Reflections of Exponential Functions",
        "Translations of Exponential Functions",
        "Exponential Functions with Radical Bases", "Geometric Sequences"
      ]
    },
    "Polynomial Expressions": {
      "Notes": [
        "Introduction to Polynomials", "Adding and Subtracting Polynomials",
        "Multiplying Monomials and Binomials",
        "Multiplying Polynomials and Simplifying Expressions",
        "Factoring Polynomials: GCF", "Factoring Polynomials: Double Grouping",
        "Factoring Trinomials: a = 1",
        "Factoring Trinomials: a = 1 (continued)",
        "Factoring Trinomials: a > 1",
        "Factoring Polynomials: Difference of Squares",
        "Factoring Polynomials: Sum and Difference of Cubes",
        "Factoring Polynomials Completely"
      ]
    },
    "Quadratic Functions": {
      "Notes": [
        "Introduction to Quadratic Functions",
        "Quadratic Functions: Standard Form",
        "Quadratic Functions: Factored Form",
        "Quadratic Functions: Vertex Form", "Completing the Square",
        "Completing the Square (continued)",
        "Modeling with Quadratic Functions"
      ]
    },
    "Quadratic Equations": {
      "Notes": [
        "Solving Quadratic Equations: Zero Product Property",
        "Solving Quadratic Equations: Factoring",
        "Solving Quadratic Equations: Square Root Property",
        "Solving Quadratic Equations: Completing the Square",
        "Solving Quadratic Equations: Completing the Square (continued)",
        "Introduction to the Quadratic Formula",
        "Modeling with Quadratic Equations", "Solving Linear-Quadratic Systems"
      ]
    },
    "Data Analysis": {
      "Notes": [
        "Describing Data", "Two-Way Tables",
        "Relative Frequencies and Association", "Measures of Center",
        "Box Plots", "Standard Deviation", "Line of Best Fit",
        "Analyzing Residuals", "Strength of Correlation", "Regression Models",
        "Performance Task: Super Survey Simulator", "Cumulative Exam"
      ]
    }
  }
}
# # Usage:
# with app.app_context(
# ):  # Required if you're running this outside of a request context
#   db.create_all()
#   populate_db(json_data)


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
        user_type = session.get('role')
        # user_type = request.form.get('user_type')

        # First, check if the passwords match
        if password != confirm_password:
          flash('Passwords do not match.', 'danger')
          return redirect(f'{self.interface_path}/register', code=302)

        # Prepare the state as a JSON string
        state = json.dumps({
          'firstname': firstname,
          'lastname': lastname,
          'email': email
        })

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

      return render_template('register.html')

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
