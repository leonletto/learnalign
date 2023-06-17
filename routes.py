from flask import request, jsonify, url_for, flash, redirect, session, render_template
import subprocess
import json


def setup_routes(app, auth, User, db, Topic, interface_path, base_path):

  @app.route('/')
  def root():
    return redirect(f'{interface_path}/homepage', code=302)

  @app.route(f'{interface_path}/homepage', methods=['GET'])
  def homepage():
    return render_template(
      'homepage.html')  # homepage.html should be your homepage template

  @app.route(f'{interface_path}/logged_in', methods=['GET'])
  def logged_in():
    if 'logged_in' not in session or not session['logged_in']:
      return redirect(f'{interface_path}/login', code=302)

    username = session['username']  # retrieve the username from session

    return render_template('logged_in.html', username=username)

  @app.route(f'{interface_path}/logout', methods=['GET'])
  def logout():
    # Clear the logged_in key from the session
    session.pop('logged_in', None)
    # Redirect the user to the login page
    return redirect(url_for('login'))

  @app.route(f'{interface_path}/collect_user_info', methods=['POST'])
  def collect_user_info():
    if 'logged_in' not in session or not session['logged_in']:
      return redirect(f'{interface_path}/login', code=302)

    username = session['username']  # retrieve the username from session

    data = request.get_json()  # get the incoming data

    # Get the current user from the database
    current_user = User.query.filter_by(username=username).first()
    if current_user is None:
      flash('User not found.', 'error')  # Flash an error message
      return redirect(f'{interface_path}/learner_setup')  # Redirect to learner_setup template

    current_user.state = json.dumps(data)  # Convert the incoming data to a JSON string
    db.session.commit()  # Commit the changes

    flash('User state updated successfully.', 'success')  # Flash a success message

    return redirect(f'{interface_path}/learner_setup')  # Redirect to learner_setup template

  @app.route(f'{interface_path}/learner_setup', methods=['GET'])
  def learner_setup():
    if 'logged_in' not in session or not session['logged_in']:
      return redirect(f'{interface_path}/login', code=302)

    username = session['username']  # retrieve the username from session

    # Get the current user from the database
    current_user = User.query.filter_by(username=username).first()
    if current_user is None:
      flash('User not found.', 'error')  # Flash an error message
      return redirect(f'{interface_path}/login')  # Redirect to login page

    user_state = json.loads(current_user.state) if current_user.state else {}  # Load the current user state
    return render_template('learner_setup.html', state=user_state, username=username)

  # ... remaining routes here ...


  @app.route(f'{interface_path}/persona', methods=['GET', 'POST'])
  def persona():
    if 'logged_in' not in session or not session['logged_in']:
      return redirect(f'{interface_path}/login', code=302)

    username = session['username']  # retrieve the username from session

    if request.method == 'POST':
      persona = request.form.get('persona')
      if persona:
        session['persona'] = persona
        print(persona)
        if persona == 'learner':
          return redirect(f'{interface_path}/learner', code=302)
        elif persona == 'guardian':
          return redirect(f'{interface_path}/guardian', code=302)
        elif persona == 'creator':
          return redirect(f'{interface_path}/creator', code=302)
        else:
          return redirect(f'{interface_path}/homepage', code=302)

    return render_template('persona.html', username=username)

  @app.route(f'{interface_path}/learner', methods=['GET'])
  def learner():
    if 'logged_in' not in session or not session['logged_in']:
      return redirect(f'{interface_path}/login', code=302)

    username = session['username']  # retrieve the username from session

    return render_template('learner.html', username=username)

  @app.route(f'{interface_path}/creator', methods=['GET'])
  def creator():
    if 'logged_in' not in session or not session['logged_in']:
      return redirect(f'{interface_path}/login', code=302)
    username = session['username']  # retrieve the username from session
    return render_template('creator.html', username=username)

  @app.route(f'{interface_path}/guardian', methods=['GET'])
  def guardian():
    if 'logged_in' not in session or not session['logged_in']:
      return redirect(f'{interface_path}/login', code=302)

    username = session['username']  # retrieve the username from session

    # Create a subset of the users dictionary containing users with the logged in user as parent
    # Use User here to access the database
    # Query the database for users with the logged in user as parent
    learners_query = User.query.filter_by(parent=username).all()

    # Convert each User instance to a dictionary
    learners = [{
      "id": learner.id,
      "username": learner.username,
      "role": learner.role,
      "parent": learner.parent
    } for learner in learners_query]
    # learners = {
    #   user: info
    #   for user, info in users.items()
    #   if 'parent' in info and info['parent'] == username
    # }
    print(learners)
    return render_template('guardian.html',
                           username=username,
                           learners=learners)

  @app.route('/topics/<int:topic_id>', methods=['GET', 'POST'])
  def edit_topic(topic_id):
      topic = Topic.query.get_or_404(topic_id)
      if request.method == 'POST':
          topic.name = request.form.get('name')
          topic.notes = request.form.get('notes')
          db.session.commit()
          return redirect(url_for('edit_topic', topic_id=topic.id))
      return render_template('edit_topic.html', topic=topic)

  @app.route(f'{base_path}/<path:path>', methods=['GET', 'POST'])
  def catch_all(path):
    print('Headers:', request.headers)
    print('Body:', request.get_data())
    print('Path:', path)
    return 'Catch all route'

  # All the other routes go here in the same manner

  return app
