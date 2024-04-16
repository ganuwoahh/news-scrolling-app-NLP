from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from cachetools import LRUCache
from random import randint
from sqlalchemy.sql.expression import func
import random
import pandas as pd

data = pd.read_csv(r'C:\Users\scxrp\Downloads\sem_6\nlp\project\website\static\real_cleaned_news_data_2.tsv', sep='\t', encoding='ISO-8859-1')

views = Blueprint('views', __name__)
auth = Blueprint('auth', __name__)

@auth.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
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
    
    images = [
    "https://i.ibb.co/23yppmv/bollywood.png",
    "https://i.ibb.co/d4RLr2K/politics.png",
    "https://i.ibb.co/v3JP3f8/sports.png",
    ]
    return render_template("index.html", user=current_user, images = images)

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
    random_row = data.sample(1).iloc[0]
    topic = random_row['topic'].lower()
    title = random_row['title']
    link = random_row['link']
    
    photo_number = random.randint(1, 10)
    photo_path = f'static/tozip_photos/{topic}_{photo_number}.jpg'

    return jsonify(title=title, photo=photo_path, link=link)

@views.route('/send-feedback', methods=['POST'])
def send_feedback():
    data = request.json
    if data and 'title' in data and 'link' in data and 'rating' in data:
        title = data['title']
        link = data['link']
        rating = data['rating']
        
        print(f'Received feedback: Title: {title}, Link: {link}, Rating: {rating}')

        return jsonify(message='Feedback received'), 200
    else:
        return jsonify(error='Invalid data'), 400
