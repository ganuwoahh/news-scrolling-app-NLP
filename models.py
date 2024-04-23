from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    nation_prob = db.Column(db.Float, nullable=False, default=0.125)
    finance_prob = db.Column(db.Float, nullable=False, default=0.125)
    world_prob = db.Column(db.Float, nullable=False, default=0.125)
    science_prob = db.Column(db.Float, nullable=False, default=0.125)
    health_prob = db.Column(db.Float, nullable=False, default=0.125)
    business_prob = db.Column(db.Float, nullable=False, default=0.125)
    technology_prob = db.Column(db.Float, nullable=False, default=0.125)
    sports_prob = db.Column(db.Float, nullable=False, default=0.125)