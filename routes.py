from flask import request, jsonify, url_for, flash, redirect, session, render_template
import subprocess
from story_teller import get_story, request_speach, get_speach, stories
import json
import time
import random


def setup_routes(app, auth, User, db, Topic, interface_path, base_path):

  @app.route('/')
  def root():
    return redirect(f'{interface_path}/homepage', code=302)

  @app.route(f'{interface_path}/homepage', methods=['GET'])
  def homepage():
    return render_template('homepage.html')

  @app.route(f'{interface_path}/parent', methods=['GET'])
  def parent():
    return render_template('parent.html')

  @app.route(f'{interface_path}/dashboard', methods=['GET'])
  def dashboard():
    return render_template('dashboard.html')

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
    return redirect(f'{interface_path}/homepage', code=302)

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
      return redirect(f'{interface_path}/learner_setup'
                      )  # Redirect to learner_setup template

    current_user.state = json.dumps(
      data)  # Convert the incoming data to a JSON string
    db.session.commit()  # Commit the changes

    flash('User state updated successfully.',
          'success')  # Flash a success message

    return redirect(
      f'{interface_path}/learner_setup')  # Redirect to learner_setup template

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

    user_state = json.loads(current_user.state) if current_user.state else {
    }  # Load the current user state
    return render_template('learner_setup.html',
                           state=user_state,
                           username=username)

  # ... remaining routes here ...

  @app.route('/get_topics', methods=['GET'])
  def get_topics():
    course = request.args.get('course', default=1, type=str)
    # Here is where you need to implement the logic to fetch the topics based on the selected course
    topics = Topic.query.filter(Topic.parent_id == course).all()
    return jsonify([{'id': topic.id, 'name': topic.name} for topic in topics])

  @app.route(f'{interface_path}/get_favorites', methods=['GET'])
  def get_favorites():
    # Check if the user is logged in
    if 'logged_in' not in session or not session['logged_in']:
      return redirect(f'{interface_path}/login', code=302)

    # Retrieve the username from the session
    username = session['username']

    # Query the User table to retrieve the user's favorites
    user = User.query.filter_by(username=username).first()

    user_state = json.loads(user.state) if user.state else {}

    print(user_state, username)

    ids = user_state.get('favorites', {})
    favorites = []

    for story_id in ids:
      story = stories[story_id]['story']
      url = stories[story_id]['url']
      favorites.append({"story": story, "url": url})

    return render_template(
      'get_favorites.html',
      favorites=favorites,
    )

  @app.route(f'{interface_path}/learning_tracks', methods=['GET', 'POST'])
  def learning_tracks():
    print(session)
    if 'logged_in' not in session or not session['logged_in']:
      return redirect(f'{interface_path}/login', code=302)

    topics = Topic.query.all()

    username = session['username']  # retrieve the username from session

    if request.method == 'POST':
      track = request.form.get('track')
      if track:
        session['track'] = track
        if track == 'story':
          return redirect(f'{interface_path}/story', code=302)
        elif track == 'tutorial':
          return redirect(f'{interface_path}/tutorial', code=302)
        else:
          return redirect(f'{interface_path}/homepage', code=302)

    return render_template('learning_tracks.html',
                           username=username,
                           topics=topics)

  @app.route(f'{interface_path}/story', methods=['GET', 'POST'])
  def story():
    if 'logged_in' not in session or not session['logged_in']:
      return redirect(f'{interface_path}/login', code=302)

    story_id = random.randint(1, 10)
    story_text = stories[str(story_id)]['story']
    audio_url = stories[str(story_id)]['url']
    username = session['username']  # retrieve the username from session

    # current_user = User.query.filter_by(username=username).first()
    # agenda = {"course": "Math", "topic": "Quadratic Functions", "subtopic": ""}
    # story_text = get_story(json.loads(current_user.state), agenda)
    # job_id, status = request_speach(story_text)
    # while status != 'success':
    #   time.sleep(5)
    #   audio_url, status = get_speach(job_id)
    # story_text = "This is a sample story text"  # Replace this with your actual story text
    # audio_url = "https://my-s3-bucket.s3.amazonaws.com/my-audio-file.mp3"  # Replace with your actual audio file URL
    return render_template('story.html',
                           story=story_text,
                           audio_url=audio_url,
                           story_id=story_id,
                           username=username)

  @app.route('/favorite_story', methods=['POST'])
  def favorite_story():
    # Get the story and story_url from the form submission
    story_id = request.form.get('story_id')
    story = stories[story_id]['story']
    url = stories[story_id]['url']
    username = session['username']
    user = User.query.filter_by(username=username).first()

    user_dict = {
      'id': user.id,
      'username': user.username,
      'password': user.password,
      'role': user.role,
      'parent': user.parent,
      'state': json.loads(user.state) if user.state else {}
    }
    # Add the story and story_url to the user's state in the database

    favorites = set(user_dict['state'].get('favorites', []))
    favorites.add(story_id)

    user_dict['state']['favorites'] = list(favorites)
    user.state = json.dumps(user_dict['state'])

    db.session.commit()

    # Redirect back to the original page or any other desired page
    return render_template('story.html',
                           story=story,
                           audio_url=url,
                           story_id=story_id,
                           username=username)

  @app.route('/favorite_video', methods=['POST'])
  def favorite_video():
    if 'logged_in' not in session or not session['logged_in']:
      return redirect(f'{interface_path}/login')
    # Redirect back to the original page or any other desired page
    username = session['username']  # retrieve the username from session

    return render_template('tutorial.html', username=username)

  @app.route(f'{interface_path}/tutorial', methods=['GET', 'POST'])
  def tutorial():
    if 'logged_in' not in session or not session['logged_in']:
      return redirect(f'{interface_path}/login')
    print(request.form)

    course = request.form.get('course')
    topic = request.form.get('topic')
    track = request.form.get('track')
    print(course, topic, track)

    username = session['username']  # retrieve the username from session

    return render_template('tutorial.html', username=username)

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

  @app.route(f'{interface_path}/about_us', methods=['GET'])
  def about_us():
    return render_template('about_us.html')

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
