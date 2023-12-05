from app import app, db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(100), unique=True, nullable=False)
    email       = db.Column(db.String(120), unique=True, nullable=False)
    password    = db.Column(db.String(100), nullable=False)
    
    # Relationships
    recipes         = db.relationship('Recipe', backref='author', lazy=True)
    interactions    = db.relationship('Interaction', backref='user', lazy=True)

    recipes_created = db.relationship('Recipe', backref='creator', lazy='dynamic')

class Recipe(db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    title               = db.Column(db.String(100), nullable=False)
    cuisine             = db.Column(db.String(30), nullable=False)
    difficulty          = db.Column(db.String(30), nullable=False)
    prep_time           = db.Column(db.Integer, nullable=False)
    cook_time           = db.Column(db.Integer, nullable=False)
    ingredients         = db.Column(db.String(60), nullable=False)
    preparation_steps   = db.Column(db.Text, nullable=False)
    image               = db.Column(db.String(255), nullable=False)  # File path or URL to image
    date_stamp          = db.Column(db.DateTime, default=datetime.utcnow)
    user_id             = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    interactions     = db.relationship('Interaction', backref='recipe', lazy=True)

    def created_by(self, user):
        return self.creator == user

class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)  # Rating value, optional
    text = db.Column(db.Text)  # Comment text, optional
    date_stamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

    def __init__(self, user_id, recipe_id, value=None, text=None):
        self.user_id = user_id
        self.recipe_id = recipe_id
        self.value = value
        self.text = text
        self.date_stamp = datetime.utcnow()
