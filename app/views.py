import os
import copy
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from app import app, bcrypt, db
from app.models import User, Recipe, Interaction
from app.forms import LoginForm, SignupForm
from flask_login import login_user, logout_user, login_required, current_user
from app import login_manager
from random import choice


# Observer Pattern for live user feedback
class NewInteraction:
    def __init__(self):
        # Initialize the list of observers and data storage
        self._observers = []  # Initialize an empty list
        self.data = {}  # Dictionary to store data related to observers
    
    def join(self, observer):
        # Add observer to the list if it's not already present
        if observer not in self._observers:
            self._observers.append(observer)
            # Initialize the data for the observer to None
            self.data[observer] = None  # Initialize data to None
    
    def left(self, observer):
        # Remove observer from the list if it exists
        try:
            self._observers.remove(observer)
            # Remove observer's data when they leave
            del self.data[observer]
        except ValueError:
            pass  # Observer not found
    
    def update(self, observer, new_interaction):
        # Update observer's data with new interaction if observer exists
        if observer in self._observers:
            self.data[observer] = new_interaction

# Singleton Pattern for user authentication
class UserAuthentication:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def login(self, username, password):
        # Implement your login logic here using SQLAlchemy and the Users model
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            new_interaction.join(current_user.id)
            return True
        return False

    def signup(self, username, email, password):
        # Implement your signup logic here using SQLAlchemy and the Users model
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return True

    def logout(self):
        new_interaction.left(current_user.id)
        logout_user()
        return True

# Factory method to create different types of recipes based on attributes
def create_recipe(title, cuisine, difficulty, prep_time, cook_time, ingredients, preparation_steps, image, user_id):
    if cuisine.lower() == 'italian':
        # Create Italian recipe
        return Recipe(title=title, cuisine=cuisine, difficulty=difficulty, prep_time=prep_time,
                      cook_time=cook_time, ingredients=ingredients, preparation_steps=preparation_steps,
                      image=image, user_id=user_id)
    elif cuisine.lower() == 'indian':
        # Create Indian recipe
        return Recipe(title=title, cuisine=cuisine, difficulty=difficulty, prep_time=prep_time,
                      cook_time=cook_time, ingredients=ingredients, preparation_steps=preparation_steps,
                      image=image, user_id=user_id)
    else:
        # Create a generic recipe for other cuisines
        return Recipe(title=title, cuisine=cuisine, difficulty=difficulty, prep_time=prep_time,
                      cook_time=cook_time, ingredients=ingredients, preparation_steps=preparation_steps,
                      image=image, user_id=user_id)

# Strategy Pattern for Recipe Recommendations
class RecommendationStrategy:
    def recommend(self, recipes, user):
        pass  # Base class for recommendation strategies

class PersonalHistoryStrategy(RecommendationStrategy):
    def recommend(self, recipes, user):
        user_ratings = user.interactions  # Assuming the user has a relationship with comments
        if user_ratings:

            # Combine user's liked recipes and commented recipes
            user_history = set(user_ratings.value).union(set(user_ratings.text))
        else:
            user_history = []

        # Filter recipes not in user's history and recommend top 5
        recommended_recipes = [recipe for recipe in recipes if recipe not in user_history][:5]
        return recommended_recipes

class TrendingRecipesStrategy(RecommendationStrategy):
    def recommend(self, recipes, user):
        # Implement recommendation based on trending recipes
        # Logic to recommend based on the most recent or fastest-growing recipes
        return sorted(recipes, key=lambda x: x.date_stamp, reverse=True)[:5]  # Example logic


auth = UserAuthentication()
new_interaction = NewInteraction()


@login_manager.user_loader
def load_user(user_id):
    # Implement your user loader logic here
    return User.query.get(int(user_id)) if user_id else None

# common params for every page
@app.context_processor
def common_parameters():
    username = None
    user_id = None
    logged_in=current_user.is_authenticated
    if logged_in:
        username = current_user.username
        user_id = current_user.id
    return dict(username=username, user_id=user_id, logged_in=logged_in)


# home view
@app.route('/')
@app.route('/home')
def index():
    if current_user.is_authenticated:
        # User is logged in, perform necessary actions
        return render_template('index.html', user=current_user)
    else:
        # User is not logged in, handle accordingly
        return render_template('index.html', user=None)


# login view
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if auth.login(username, password):
            return redirect(url_for('index'))  # Replace 'index' with your landing page
        else:
            flash('Login unsuccessful. Please check your credentials.', 'danger')
    return render_template('login.html', title='Login', form=form)


# signup view
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        if auth.signup(username, email, password):
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))  # Redirect to login after successful signup
        else:
            flash('Username already exists. Please choose a different username.', 'danger')
    return render_template('signup.html', title='Sign Up', form=form)


# logout view
@app.route('/logout')
@login_required
def logout():
    auth.logout()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))  # Redirect to login after logout


# profile view
@app.route('/profile')
@login_required
def profile():
    # Assuming your User model has fields like 'username', 'email', etc.
    user = current_user  # Get the current logged-in user

    return render_template('profile.html', user=user)


# explore view
@app.route('/explore')
@login_required
def explore():
    recipes = Recipe.query.all()  # Fetch all recipes from the database

    strategies = {
        'Personal History': PersonalHistoryStrategy(),
        'Trending Recipes': TrendingRecipesStrategy()
    }

    chosen_strategy = choice(list(strategies.values()))  # Randomly pick a strategy for demonstration

    recommended_recipes = chosen_strategy.recommend(recipes, current_user)

    return render_template('explore.html', recommended_recipes=recommended_recipes)


# add recipe view
@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        title = request.form.get('title')
        cuisine = request.form.get('cuisine')
        difficulty = request.form.get('difficulty')
        prep_time = int(request.form.get('prep_time'))
        cook_time = int(request.form.get('cook_time'))
        ingredients = request.form.get('ingredients')
        preparation_steps = request.form.get('preparation_steps')
        image = request.form.get('image')

        # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)  # Set your upload folder path
                image.save(image_path)  # Save the uploaded image to the specified path
                image_url = image.filename  # Set image URL/path as needed
        else:
            image_url = 'default_recipe_image.png'
        
        # Get the user_id
        user_id = current_user.id if current_user.is_authenticated else None

        # Factory method pattern for creating different types of recipes
        recipe = create_recipe(title, cuisine, difficulty, prep_time, cook_time, ingredients, preparation_steps, image_url, user_id)

        # Save the created recipe to the database
        db.session.add(recipe)
        db.session.commit()

        return redirect(url_for('view_recipe', recipe_id=recipe.id))

    return render_template('add_recipe.html', title='Add Recipe')


# view recipe view
@app.route('/explore/<int:recipe_id>')
@login_required
def view_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    creator_id = recipe.user_id
    creator_name = User.query.get(creator_id).username
    if not recipe:
        abort(404)

    interactions = recipe.interactions

    return render_template('view_recipe.html', creator_name=creator_name, recipe=recipe, interactions=interactions)


# add interaction - ratings and comments
@app.route('/add_interaction/<int:recipe_id>', methods=['POST'])
@login_required
def add_interaction(recipe_id):
    rating = int(request.form.get('value'))
    comment = request.form.get('comment')

    if rating == '' and comment == '':
        return redirect(url_for('view_recipe', logged_in=current_user.is_authenticated, recipe_id=recipe_id))

    # Find the associated recipe
    recipe = Recipe.query.get_or_404(recipe_id)

    # Get the user_id (assuming user is logged in)
    user_id = current_user.id if current_user.is_authenticated else None

    interaction = Interaction(value=rating, text=comment, recipe_id=recipe_id, user_id=user_id)

    # Add the new interaction to the database
    db.session.add(interaction)
    db.session.commit()

    # Get the user ID of the recipe creator
    creator_id = Recipe.query.filter_by(id=recipe_id).first().user_id

    if creator_id != current_user.id:
        notify_recipe_creator(recipe_id, user_id, creator_id)

    # Redirect back to the recipe details page after adding the interaction
    return redirect(url_for('view_recipe', recipe_id=recipe_id))


# Function to notify recipe creator when a new interaction occurs
def notify_recipe_creator(recipe_id, user_id, creator_id):
    if recipe_id and user_id:
        username = User.query.filter_by(id=user_id).first().username
        recipe = Recipe.query.filter_by(id=recipe_id).first().title
        data = {'username': username, 'recipe': recipe, 'recipe_id': recipe_id, 'user_id': user_id}

        new_interaction.update(creator_id, data)


# get updates view
@app.route('/get_updates/<int:user_id>', methods=['GET'])
def get_updates(user_id):
    if user_id in new_interaction.data:
        dup = copy.deepcopy(new_interaction.data[user_id])
        new_interaction.data[user_id] = False
        return jsonify({'user_id': user_id, 'update': dup})
    else:
        return jsonify({'user_id': user_id, 'update': False})

