from flask import Blueprint, render_template, request

# If you're not using application factory pattern, you might directly import app instead of db
# from your_application import app

home_blueprint = Blueprint('home', __name__, template_folder='templates')

images = [
    "https://i.ibb.co/23yppmv/bollywood.png",
    "https://i.ibb.co/d4RLr2K/politics.png",
    "https://i.ibb.co/v3JP3f8/sports.png",
]

@home_blueprint.route('/home')
def index():
    return render_template('index.html', images=images)

@home_blueprint.route('/home/like', methods=['POST'])
def like():
    data = request.json
    if data and data.get('liked'):
        print('Image liked!')
    return '', 204  # 204 No Content

@home_blueprint.route('/home/dislike', methods=['POST'])
def dislike():
    data = request.json
    if data and data.get('disliked'):
        print('Image disliked!')
    return '', 204
