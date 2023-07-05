# used to setup the database for the first time and populate it with data


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

users = {
  "admin": {
    "password": "learnalign",
    "role": "admin"
  },
  "cathy": {
    "password": "password",
    "role": "parent"
  },
  "joey": {
    "password": "password",
    "role": "student",
    "parent": "cathy"
  },
  "mike": {
    "password": "password",
    "role": "student"
  },
  "mary": {
    "password": "password",
    "role": "content"
  },
}


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


# # Usage:
# with app.app_context(
# ):  # Required if you're running this outside of a request context
#   db.create_all()
#   populate_db(json_data)

# with app.app_context(
# ):  # Required if you're running this outside of a request context
#   db.create_all()

#   for username, data in users.items():
#     user = User.query.filter_by(username=username).first()
#     if not user:
#       new_user = User(username=username,
#                       password=data["password"],
#                       role=data["role"])
#       if "parent" in data:
#         new_user.parent = data["parent"]
#       db.session.add(new_user)

#   db.session.commit()
