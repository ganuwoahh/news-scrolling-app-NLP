from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from cachetools import LRUCache
from random import choices
from sqlalchemy.sql.expression import func
import random
import pandas as pd
import logging

data = pd.read_excel(r'C:\Users\scxrp\Downloads\sem_6\nlp\project\website\static\demo.xlsx')

views = Blueprint('views', __name__)
auth = Blueprint('auth', __name__)

@auth.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
         
        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Password!', category='error')
        else:
            flash('No user exists!', category='error')
        
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('User already exists!', category='error')
        elif (not username) or (len(username) < 2) or (password1 != password2) or (not password1) or (len(password1) < 7):
            flash('Invalid input. Please check your data.', category='error')
        else:
            new_user = User(
                username=username,
                password=password1
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@views.route('/home', methods=['GET', 'POST'])
@login_required
def index():
    return render_template("index.html", user=current_user)

@views.route('/home/like', methods=['POST'])
def like():
    data = request.json
    if data and data.get('liked'):
        print('Image liked!')
    return '', 204

@views.route('/home/dislike', methods=['POST'])
def dislike():
    data = request.json
    if data and data.get('disliked'):
        print('Image disliked!')
    return '', 204

@views.route('/get_random_title')
def get_random_title():
    # Retrieve the current user's probabilities from the database
    user = User.query.filter_by(username=current_user.username).first()
    
    # Extract probabilities from the user object
    probabilities = [
        user.nation_prob, user.finance_prob, user.world_prob,
        user.science_prob, user.health_prob, user.business_prob,
        user.technology_prob, user.sports_prob
    ]
    
    # Topics corresponding to the probabilities
    topics = [
        'nation', 'finance', 'world', 'science',
        'health', 'business', 'technology', 'sports'
    ]
    
    # Choose a topic based on the probabilities
    chosen_topic = choices(topics, probabilities)[0]
    
    logging.info(f"Chosen topic: {chosen_topic.upper()}")  # Add logging to check the chosen topic
    
    # Retrieve rows from the database that match the chosen topic
    topic_data = data[data['topic'] == chosen_topic.upper()]
    
    # Check if there are any rows for the chosen topic
    if topic_data.empty:
        logging.error(f"No data found for topic: {chosen_topic}")
        return jsonify(error="No data found for chosen topic"), 404
    
    # Select a random row from the topic data
    random_row = topic_data.sample(1).iloc[0]
    
    # Extract data from the random row
    title = random_row['title']
    link = random_row['link']
    photo_number = random.randint(1, 10)  # Assuming photo numbers are still used
    photo_path = f"static/tozip_photos/{chosen_topic}_{photo_number}.jpg"

    # Return the randomly selected title along with other data
    return jsonify(title=title, photo=photo_path, link=link, topic=chosen_topic)

@views.route('/protected')
@login_required
def protected_route():
    
    user_id = current_user.id
    username = current_user.username
    
    return f'Current User ID: {user_id}, Username: {username}'

@views.route('/send-feedback', methods=['POST'])
@login_required
def send_feedback():
    def calculate_updated_probabilities(initial_probabilities, rating, rated_topic):
        # Define the minimum and maximum probabilities for a topic
        min_probability = 0.0125  # 1.25%
        max_probability = 0.3  # 30%
        
        # Define the weight change for the rated topic
        weight_change = 0.02  # Adjust as needed
        
        if rating == 0.7:  # Dislike rating
            weight_change *= -1  # Decrease weight for disliked topic
        
        # Calculate the new total weight for normalization
        total_weight = sum(initial_probabilities.values()) + weight_change
        
        # Calculate the new probabilities
        updated_probabilities = {}
        for topic, probability in initial_probabilities.items():
            if topic == rated_topic:
                updated_probabilities[topic] = max(min(probability + weight_change, max_probability), min_probability)
            else:
                updated_probabilities[topic] = max(min(probability - weight_change / (len(initial_probabilities) - 1), max_probability), min_probability)
        
        # Normalize the probabilities
        updated_probabilities = {topic: prob / total_weight for topic, prob in updated_probabilities.items()}
        
        return updated_probabilities

    
    data = request.json
    if data and 'title' in data and 'link' in data and 'rating' in data and 'topic' in data:
        title = data['title']
        link = data['link']
        rating = data['rating']
        rated_topic = data['topic']  # Retrieve the rated topic from the request
        
        # Assign the current user to the user variable
        user = current_user
        
        # Check if current_user is available
        print(f"Current User ID: {user.id}, Username: {user.username}")
        
        # Define the initial probabilities
        initial_probabilities = {
            'nation': user.nation_prob,
            'finance': user.finance_prob,
            'world': user.world_prob,
            'science': user.science_prob,
            'health': user.health_prob,
            'business': user.business_prob,
            'technology': user.technology_prob,
            'sports': user.sports_prob
        }
        
        # Calculate the new probabilities based on user feedback
        updated_probabilities = calculate_updated_probabilities(initial_probabilities, rating, rated_topic)
        
        # Update the user's probabilities in the database
        user.nation_prob = updated_probabilities['nation']
        user.finance_prob = updated_probabilities['finance']
        user.world_prob = updated_probabilities['world']
        user.science_prob = updated_probabilities['science']
        user.health_prob = updated_probabilities['health']
        user.business_prob = updated_probabilities['business']
        user.technology_prob = updated_probabilities['technology']
        user.sports_prob = updated_probabilities['sports']
        
        # Commit the changes to the database
        db.session.commit()
        
        print(f'Received feedback: Title: {title}, Link: {link}, Rating: {rating}, Rated Topic: {rated_topic}')
        
        return jsonify(message='Feedback received'), 200
    else:
        return jsonify(error='Invalid data'), 400
